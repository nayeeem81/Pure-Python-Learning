# api/texteditor.py

from typing import List, Set 
import os
import json
import traceback
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel
from sqlmodel import select, func, delete
from sqlmodel.ext.asyncio.session import AsyncSession
from data.database import get_db 
from data.model import Sentence  
from pathlib import Path
from datetime import datetime, timezone
# Assuming your models and engine setup are imported
from data.model import Story, get_session 

router_storygrid = APIRouter(tags=["Text Edit & DSP"])

WORKSPACE_DIR = os.path.abspath("./project")
GENERATED_DIR = os.path.join(WORKSPACE_DIR, "generated")

class BulkDeleteRequest(BaseModel):
	ids: List[int]

# ==============================================================
# PRIVATE UTILITY HELPERS (Enforces DRY Principle)
# ==============================================================
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

def _cleanup_physical_files(relative_paths: Set[str]) -> None:
	print(f"\n=== STARTING FILE CLEANUP SYSTEM DISK SCAN ===")
	for relative_path in relative_paths:
		if relative_path and relative_path != "#":
			# 1. Assemble the path
			full_file_path = os.path.normpath(
				os.path.join(WORKSPACE_DIR, relative_path.replace("generated/", ""))
			)
			
			print(f"Checking target location: {full_file_path}")
			
			# 2. Verify visibility checks
			if os.path.exists(full_file_path):
				try:
					os.remove(full_file_path)
					print(f"🔥 SUCCESS: Deleted file from hard drive: {full_file_path}")
				except Exception as disk_err:
					print(f"❌ ERROR: File found, but system blocked deletion: {disk_err}")
			else:
				print(f"⚠️ NOT FOUND: Python could not find a file matching this path.")
	print(f"=== END OF FILE CLEANUP SYSTEM DISK SCAN ===\n")

# ==============================================================
# CORE API ENDPOINTS
# ==============================================================
@router_storygrid.get("/sentences", response_model=dict)
async def get_storygrid(
	session: AsyncSession = Depends(get_db),
	skip: int = Query(default=0, ge=0),
	limit: int = Query(default=10, le=100)
): 
	try:
		count_statement = select(func.count()).select_from(Sentence)
		count_result = await session.execute(count_statement)
		total_records = count_result.scalar() or 0
		
		statement = select(Sentence).order_by(Sentence.id).offset(skip).limit(limit) 
		result = await session.execute(statement) 
		sentences = result.scalars().all()
		
		cleaned_sentences = []
		for s in sentences:
			sentence_dict = s.model_dump()
			text_val = "No Text Found"
			mp3_val = ""
			total_duration_seconds = ""

			if hasattr(s, "original_sentence_json") and s.original_sentence_json:
				json_data = s.original_sentence_json
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
				if hasattr(s, "text_content") and s.text_content:
					text_val = s.text_content
				elif hasattr(s, "original_sentence") and s.original_sentence:
					text_val = s.original_sentence

			if not mp3_val:
				if hasattr(s, "mp3_file_path") and s.mp3_file_path:
					mp3_val = s.mp3_file_path
					
			if not total_duration_seconds:
				if hasattr(s, "total_duration_seconds") and s.total_duration_seconds:
					total_duration_seconds = s.total_duration_seconds
					
			sentence_dict["text_content"] = text_val
			sentence_dict["master_mp3_path"] = mp3_val
			sentence_dict["total_duration_seconds"] = total_duration_seconds

			if "audio_bytes" in sentence_dict:
				sentence_dict["audio_bytes"] = None 

			# Correctly appended inside the loop scope block
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


@router_storygrid.delete("/sentences/{id}", status_code=status.HTTP_200_OK)
async def delete_single_router_storygrid(id: int, session: AsyncSession = Depends(get_db)):
	try:
		statement = select(Sentence).where(Sentence.id == id)
		result = await session.execute(statement)
		sentence = result.scalars().first()
		if not sentence:
			raise HTTPException(status_code=404, detail=f"Sentence ID {id} not found in database records.")

		# Extract paths and delete matching disk assets
		paths_to_delete = _extract_file_paths(sentence)
		_cleanup_physical_files(paths_to_delete)

		await session.delete(sentence)
		await session.commit()
		return {"status": "success", "message": f"Sentence tracking row {id} and files cleared successfully."}

	except HTTPException:
		raise
	except Exception as e:
		await session.rollback()
		print("=== SINGLE DELETION EXCEPTION STACK ===")
		traceback.print_exc()
		print("========================================")
		raise HTTPException(status_code=500, detail=f"Internal database deletion failure: {str(e)}")


@router_storygrid.post("/sentences/bulk-delete", status_code=status.HTTP_200_OK)
async def bulk_delete_storygrid(payload: BulkDeleteRequest, session: AsyncSession = Depends(get_db)):
	try:
		if not payload.ids:
			return {"status": "ignored", "message": "No targets passed."}

		# Fetch records matching target IDs
		statement = select(Sentence).where(Sentence.id.in_(payload.ids))
		result = await session.execute(statement)
		sentences_to_clear = result.scalars().all()

		if not sentences_to_clear:
			return {"status": "success", "message": "No records found."}

		# Aggregate unique file paths across all matched sentences
		all_paths_to_delete = set()
		for sentence in sentences_to_clear:
			all_paths_to_delete.update(_extract_file_paths(sentence))

		# Wipe local hard drive disk dependencies safely in one go
		_cleanup_physical_files(all_paths_to_delete)

		# High-performance bulk database deletion execution step
		delete_statement = delete(Sentence).where(Sentence.id.in_(payload.ids))
		await session.execute(delete_statement)

		await session.commit()
		return {"status": "success", "message": "Successfully dropped records."}

	except Exception as e:
		await session.rollback()
		print("=== BULK DELETION EXCEPTION STACK ===")
		traceback.print_exc()
		print("======================================")
		raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# ==============================================================
# DATA MODELS
# ==============================================================
class Story(BaseModel):
   story_name: str

@router_storygrid.post("/story", status_code=status.HTTP_201_CREATED)
async def create_story(story: Story, db: AsyncSession = Depends(get_db)):
    try:
		story = Story(
			story_name=story.story_name,
			story_absolute_folderpath=story.story_name
		)

		new_words.append(word_item)
        
        db.add_all(new_words)

        await db.commit() 

        return {"message": f"Successfully compiled {len(new_words)} words for Sentence #{sentence_id}."}

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while parsing the text layout: {str(e)}"
        )


@app.post("/stories/", response_model=Story)
def create_story(story_name: str, session: Session = Depends(get_session)):
    # 1. Create the physical file system folder
    try:
        user_home = Path.home()
        project_dir = user_home / "Documents" / "Project"
        project_dir.mkdir(parents=True, exist_ok=True)

        story_dir = project_dir / story_name
        story_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert path object to string for the database
        absolute_path_str = str(story_dir)
        
    except PermissionError:
        raise HTTPException(status_code=403, detail="File system write permission denied.")

    # 2. Build the database record
    now = datetime.now(timezone.utc)
    new_story = Story(
        story_name=story_name,
        story_absolute_folderpath=absolute_path_str,
        modified_at=now.date(),
		modified_by=now.date()
    )

    # 3. Save to PostgreSQL
    session.add(new_story)
    session.commit()
    session.refresh(new_story)
    return new_story


@app.get("/stories/{story_id}/files")
def browse_story_files(story_id: int, session: Session = Depends(get_session)):
    # 1. Get the story from the database
    story = session.get(Story, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    # 2. Turn the saved string path back into a Path object
    story_folder = Path(story.story_absolute_folderpath)

    # 3. Safety check: make sure the folder wasn't deleted manually on Windows
    if not story_folder.is_dir():
        raise HTTPException(status_code=404, detail="The physical directory does not exist on disk.")

    # 4. Browse and list all files inside (e.g., mp3s, texts, chapters)
    found_files = []
    for file_path in story_folder.iterdir():
        if file_path.is_file(): # Skip inner folders, only grab files
            found_files.append({
                "filename": file_path.name,
                "extension": file_path.suffix,
                "size_bytes": file_path.stat().st_size
            })

    return {
        "story_name": story.story_name,
        "folder_path": story.story_absolute_folderpath,
        "files": found_files
    }
