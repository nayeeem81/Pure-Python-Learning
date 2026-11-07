import os
import json
import shutil
import traceback
from typing import List, Set
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
# Database connections (Ensure these match your actual structure)
from data.database import get_db
from data.model import Sentence

router_sentence = APIRouter(tags=["Text, DSP & GTTS"])

# ==========================================================================
# 🛠️ FIXED: ALIGNED STORAGE CONFIGURATION WITH D: DRIVE PARAMS
# ==========================================================================
STORAGE_ROOT = "D:\\StudioStorage"
GENERATED_DIR = os.path.normpath(os.path.join(STORAGE_ROOT, "generated"))

class BulkDeleteRequest(BaseModel):
	ids: List[int]

def _extract_file_paths(sentence) -> Set[str]:
	"""
	Extracts all physical file paths related to a sentence object,
	parsing nested json fields and timeline tracks safely.
	"""
	extracted_paths = set()
	
	if hasattr(sentence, "mp3_file_path") and sentence.mp3_file_path:
		extracted_paths.add(sentence.mp3_file_path)

	if hasattr(sentence, "original_sentence_json") and sentence.original_sentence_json:
		json_data = sentence.original_sentence_json
		
		# Safe JSON string parse fallback handling
		if isinstance(json_data, str):
			try:
				json_data = json.loads(json_data)
			except Exception:
				json_data = {}
		
		if isinstance(json_data, dict):
			if "master_mp3_path" in json_data:
				extracted_paths.add(json_data["master_mp3_path"])
				
			if "words_timeline" in json_data and isinstance(json_data["words_timeline"], list):
				for word_entry in json_data["words_timeline"]:
					if isinstance(word_entry, dict) and "segment_file" in word_entry:
						extracted_paths.add(word_entry["segment_file"])
						
	return extracted_paths


def _cleanup_physical_files(absolute_paths: Set[str], sentence_ids: List[int] = None) -> None:
    """
    🛠️ FIXED: Standardised all loop variable structures to eliminate 'sid' NameErrors.
    Safely purges absolute media files and isolated word segment directories from the D: drive.
    """
    print(f"\n=== STARTING FILE CLEANUP SYSTEM DISK SCAN ===")
    
    # 1. Clear individual asset files (.mp3, .wav, or text blueprints)
    for path_str in absolute_paths:
        if path_str and path_str != "#":
            full_file_path = os.path.normpath(path_str)
            print(f"Checking target location: {full_file_path}")
            
            if os.path.exists(full_file_path):
                try:
                    os.remove(full_file_path)
                    print(f"🔥 SUCCESS: Deleted file from D: Drive: {full_file_path}")
                except Exception as disk_err:
                    print(f"❌ ERROR: File found, but system blocked deletion: {disk_err}")
            else:
                print(f"⚠️ NOT FOUND: Python could not find file at: {full_file_path}")
                
    # 2. Clear the dynamic sentence directories and accompanying metadata mappings
    if sentence_ids:
        # 🛠️ DOUBLE-CHECKED INITIALIZATION LOOP: Explicitly naming it 'sentence_id' to avoid conflicts
        for sentence_id in sentence_ids:
            # Drop the companion metadata mapping file if it exists
            json_meta_path = os.path.normpath(os.path.join(GENERATED_DIR, f"metadata_{sentence_id}.json"))
            if os.path.exists(json_meta_path):
                try:
                    os.remove(json_meta_path)
                    print(f"🔥 SUCCESS: Cleaned orphan metadata track: {json_meta_path}")
                except Exception:
                    pass
            
            # 🛠️ SAFE RESOLUTION: Wipes the entire sentence subfolder container out of the segments base path
            segment_dir = os.path.normpath(os.path.join(GENERATED_DIR, "segments", f"sentence_{sentence_id}"))
            if os.path.exists(segment_dir) and os.path.isdir(segment_dir):
                try:
                    shutil.rmtree(segment_dir)
                    print(f"📁 SUCCESS: Purged entire segment directory block: {segment_dir}")
                except Exception as dir_err:
                    print(f"❌ ERROR: Failed to drop directory container: {dir_err}")

    print(f"=== END OF FILE CLEANUP SYSTEM DISK SCAN ===\n")


# Optimized database payload fetch strategy
@router_sentence.get("/sentences", response_model=dict)
async def get_sentences(
	session: AsyncSession = Depends(get_db),
	skip: int = Query(default=0, ge=0),
	limit: int = Query(default=10, le=100)
): 
	try:
		if skip == 0:
			count_statement = select(func.count()).select_from(Sentence)
			count_result = await session.execute(count_statement)
			total_records = count_result.scalar() or 0
		else:
			total_records = -1 

		statement = (
			select(
				Sentence.id,
				Sentence.text_content,
				Sentence.mp3_file_path,
				Sentence.original_sentence_json,
				Sentence.modified_sentence_json,
				Sentence.version,
				Sentence.modified_at,
				Sentence.modified_by
			)
			.order_by(Sentence.id)
			.offset(skip)
			.limit(limit)
		)
		
		result = await session.execute(statement) 
		sentences = result.all()
		
		cleaned_sentences = []
		for s in sentences:
			sentence_dict = {
				"id": s.id,
				"text_content": s.text_content,
				"mp3_file_path": s.mp3_file_path,
				"original_sentence_json": s.original_sentence_json,
				"modified_sentence_json": s.modified_sentence_json,
				"version": s.version,
				"modified_at": s.modified_at,
				"modified_by": s.modified_by,
				"audio_bytes": None
			}
			
			text_val = "No Text Found"
			mp3_val = ""
			total_duration_seconds = "2.88"

			json_data = s.original_sentence_json
			if json_data:
				if isinstance(json_data, str):
					try:
						json_data = json.loads(json_data)
					except Exception:
						json_data = {}
				
				if isinstance(json_data, dict):
					text_val = json_data.get("original_sentence", text_val)
					mp3_val = json_data.get("master_mp3_path", mp3_val)
					total_duration_seconds = json_data.get("total_duration_seconds", total_duration_seconds)

			if text_val == "No Text Found":
				if s.text_content:
					text_val = s.text_content
				elif hasattr(s, "original_sentence") and getattr(s, "original_sentence"):
					text_val = s.original_sentence

			if not mp3_val and s.mp3_file_path:
				mp3_val = s.mp3_file_path
					
			if not total_duration_seconds and hasattr(s, "total_duration_seconds"):
				total_duration_seconds = getattr(s, "total_duration_seconds")
					
			sentence_dict["text_content"] = text_val
			# 🛠️ FOR FRONTEND COMPATIBILITY: If paths are absolute, extract file name for play hooks
			# e.g., converts D:\Storage\generated\sentence_1.mp3 -> generated/sentence_1.mp3
			if mp3_val and "generated" in mp3_val:
				sentence_dict["master_mp3_path"] = "generated/" + os.path.basename(mp3_val)
			else:
				sentence_dict["master_mp3_path"] = mp3_val

			sentence_dict["total_duration_seconds"] = total_duration_seconds
			cleaned_sentences.append(sentence_dict)

		return {
			"total": total_records,
			"skip": skip,
			"limit": limit,
			"data": cleaned_sentences
		}
		
	except Exception as e:
		print("=== DATABASE ERROR TRACEBACK ===")
		traceback.print_exc()
		print("=================================")
		raise HTTPException(status_code=500, detail=f"Database operational crash: {str(e)}")


@router_sentence.delete("/sentences/{id}", status_code=status.HTTP_200_OK)
async def delete_single_sentence(id: int, session: AsyncSession = Depends(get_db)):
	try:
		statement = select(Sentence).where(Sentence.id == id)
		result = await session.execute(statement)
		sentence = result.scalars().first()

		if not sentence:
			raise HTTPException(status_code=404, detail=f"Sentence ID {id} not found in database records.")

		paths_to_delete = _extract_file_paths(sentence)
		# 🛠️ FIXED: Clean up files and specific child directories using the ID parameter
		_cleanup_physical_files(paths_to_delete, [id])

		await session.delete(sentence)
		await session.commit()
		return {"status": "success", "message": f"Sentence tracking row {id} and files cleared successfully."}

	except HTTPException:
		raise
	except Exception as e:
		await session.rollback()
		print("=== SINGLE DELETION EXCEPTION STACK ===")
		traceback.print_exc()
		raise HTTPException(status_code=500, detail=f"Internal database deletion failure: {str(e)}")


# ==========================================================================
# FILE LOCATION: api/sentence.py -> bulk_delete_sentences()
# ==========================================================================

@router_sentence.post("/sentences/bulk-delete", status_code=status.HTTP_200_OK)
async def bulk_delete_sentences(payload: BulkDeleteRequest, session: AsyncSession = Depends(get_db)):
    """
    🛠️ FIXED: Removed the internal 'sid' NameError variable leak inside the mapping iteration loop.
    Recursively clears D: drive storage footprints and strips target records out of PostgreSQL cleanly.
    """
    try:
        if not payload.ids:
            return {"status": "ignored", "message": "No targets passed."}

        # Fetch records matching target IDs
        statement = select(Sentence).where(Sentence.id.in_(payload.ids))
        result = await session.execute(statement)
        sentences_to_clear = result.scalars().all()

        if not sentences_to_clear:
            return {"status": "success", "message": "No matching database records found."}

        # Aggregate unique file paths across all matched sentences
        all_paths_to_delete = set()
        actual_cleared_ids = []

        # 🛠️ FIXED THE TRAP: Loop variable must strictly match what we process internally
        for sentence in sentences_to_clear:
            all_paths_to_delete.update(_extract_file_paths(sentence))
            actual_cleared_ids.append(int(sentence.id))

        # 1. Fire physical storage purge across targeted items (D: drive cleanup)
        _cleanup_physical_files(all_paths_to_delete, actual_cleared_ids)

        # 2. Fire structural database row purge
        for sentence in sentences_to_clear:
            await session.delete(sentence)
            
        await session.commit()
        
        return {
            "status": "success", 
            "message": f"Successfully deleted {len(actual_cleared_ids)} rows and all related physical audio/segment assets."
        }

    except Exception as e:
        await session.rollback()
        print("=== BULK DELETION EXCEPTION STACK ===")
        traceback.print_exc()
        print("======================================")
        raise HTTPException(status_code=500, detail=f"Internal database bulk deletion failure: {str(e)}")
