from sqlalchemy.orm import Session 
from pathlib import Path 
from datetime import datetime, timezone 
from typing import List, Set 
import os 
import json 
import traceback 
from fastapi import APIRouter, HTTPException, Depends, Query, status 
from pydantic import BaseModel 
from sqlmodel import select, func, delete 
from sqlmodel.ext.asyncio.session import AsyncSession 
from data.database import get_db 
# FIX: Ensure all required models (Story, Chapter) are imported here
from data.model import Sentence, Story, Chapter

router_storygrid = APIRouter(tags=["Text Edit & DSP"]) 

WORKSPACE_DIR = os.path.abspath("./project") 
GENERATED_DIR = os.path.join(WORKSPACE_DIR, "generated") 

# ============================================================== 
# PRIVATE UTILITY HELPERS 
# ============================================================== 
def _extract_file_paths(sentence) -> Set[str]: 
    """ Extracts all physical file paths related to a sentence object. """
    extracted_paths = set() 
    if hasattr(sentence, "mp3_file_path") and sentence.mp3_file_path: 
        extracted_paths.add(sentence.mp3_file_path) 
    if hasattr(sentence, "original_sentence_json") and sentence.original_sentence_json: 
        json_data = sentence.original_sentence_json 
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
            full_file_path = os.path.normpath( 
                os.path.join(WORKSPACE_DIR, relative_path.replace("generated/", "")) 
            ) 
            print(f"Checking target location: {full_file_path}") 
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
        raise HTTPException(status_code=500, detail=f"Database operational crash: {str(e)}") 

@router_storygrid.delete("/sentences/{id}", status_code=status.HTTP_200_OK) 
async def delete_single_router_storygrid(id: int, session: AsyncSession = Depends(get_db)): 
    try: 
        statement = select(Sentence).where(Sentence.id == id) 
        result = await session.execute(statement) 
        sentence = result.scalars().first() 
        if not sentence: 
            raise HTTPException(status_code=404, detail=f"Sentence ID {id} not found in database records.") 

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
        raise HTTPException(status_code=500, detail=f"Internal database deletion failure: {str(e)}") 


class BulkAddRequest(BaseModel): 
    ids: List[int] 

@router_storygrid.post("/sentences/bulk-add", status_code=status.HTTP_200_OK) 
async def bulk_add_storygrid(payload: BulkAddRequest, session: AsyncSession = Depends(get_db)): 
    try: 
        if not payload.ids: 
            return {"status": "ignored", "message": "No targets passed."} 

        statement = select(Sentence).where(Sentence.id.in_(payload.ids)) 
        result = await session.execute(statement) 
        sentences_to_clear = result.scalars().all() 
        if not sentences_to_clear: 
            return {"status": "success", "message": "No records found."} 

        all_paths_to_delete = set() 
        for sentence in sentences_to_clear: 
            all_paths_to_delete.update(_extract_file_paths(sentence)) 

        _cleanup_physical_files(all_paths_to_delete) 

        delete_statement = delete(Sentence).where(Sentence.id.in_(payload.ids)) 
        await session.execute(delete_statement) 
        await session.commit() 
        return {"status": "success", "message": "Successfully dropped records."} 
    except Exception as e: 
        await session.rollback() 
        print("=== BULK DELETION EXCEPTION STACK ===") 
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}") 

# ============================================================== 
# STORIES & CHAPTERS ENDPOINTS 
# =====================================g========================= 
class StoryCreateSchema(BaseModel): 
	story_name: str

@router_storygrid.post("/stories") 
# FIX: Switched standard Session to AsyncSession type hint
async def create_story(payload: StoryCreateSchema, session: AsyncSession = Depends(get_db)): 
    try: 
        story_name = payload.story_name 
        user_home = Path.home() 
        project_dir = user_home / "Documents" / "Project" 
        project_dir.mkdir(parents=True, exist_ok=True) 
        story_dir = project_dir / story_name 
        story_dir.mkdir(parents=True, exist_ok=True) 
        absolute_path_str = str(story_dir) 
    except PermissionError: 
        raise HTTPException(status_code=403, detail="File system write permission denied.") 

    try:
        now = datetime.now(timezone.utc) 
        new_story = Story( 
            story_name=story_name, 
            story_absolute_folderpath=absolute_path_str, 
            version=1, 
            modified_at=now, 
            modified_by="System" 
        ) 
        session.add(new_story) 
        await session.commit() 
        await session.refresh(new_story) 
        return new_story
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create story: {str(e)}")

class ChapterCreateSchema(BaseModel): 
    chapter_name: str 
    serial_number: int 
    story_id: int 

@router_storygrid.post("/chapters") 
async def create_chapter(payload: ChapterCreateSchema, session: AsyncSession = Depends(get_db)):
    chapter_name = payload.chapter_name
    serial_number = payload.serial_number
    story_id = payload.story_id
    
	# Fetch existing chapters to determine sequence and log information
    statement_story = select(Story).where(Story.id == story_id).order_by(Story.id)

    result = await session.execute(statement_story)
    all_stories = result.scalars().all()
    try:
        user_home = Path.home()
        project_dir = user_home / "Documents" / "Project" / f"{all_stories[0].story_name}" 
        project_dir.mkdir(parents=True, exist_ok=True)
        chapterdir = project_dir / f"{chapter_name}" 
        chapterdir.mkdir(parents=True, exist_ok=True)
        absolute_path_str = str(chapterdir)
    except PermissionError:
        raise HTTPException(status_code=403, detail="File system write permission denied.")
        
    try:
        # Fetch existing chapters to determine sequence and log information
        statement = select(Chapter).where(Chapter.story_id == story_id).order_by(Chapter.id)
        result = await session.execute(statement)
        all_chapters = result.scalars().all()
        
        if all_chapters:
            first_chapter = all_chapters[0]
            sequence_number = len(all_chapters) + 1
            print(f"Success! Found chapter name: {first_chapter.chapter_name}")
        else:
            sequence_number = 1
            print("No chapter matched this story_id. Starting sequence at 1.")
            
        now = datetime.now(timezone.utc)
        new_chapter = Chapter(
            chapter_name=chapter_name,
            story_id=story_id,
            # FIX 1: Assign the calculated sequence_number to the serial_number column
            serial_number=sequence_number, 
            # FIX 2: Assign the generated path string to your path column
            chapter_absolute_folderpath=absolute_path_str, 
            modified_at=now,
            modified_by="System"
        )
        
        session.add(new_chapter)
        await session.commit()
        await session.refresh(new_chapter)
        return new_chapter
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create chapter: {str(e)}")
