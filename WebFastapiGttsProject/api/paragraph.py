# 1. Standard Library Imports
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import traceback
from typing import List, Set
# 2. Third-Party Imports
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlmodel import delete, func, select
from sqlmodel.ext.asyncio.session import AsyncSession
# 3. Local Application Imports
from data.database import get_db
from data.model import AudioChapter, Chapter, Sentence, Story

router_paragraph = APIRouter(tags=["Paragraphs Grid, Delete, View Sentences, Play Mp3"]) 

WORKSPACE_DIR = os.path.abspath("./project") 
GENERATED_DIR = os.path.join(WORKSPACE_DIR, "generated") 

class SelectedItem(BaseModel):
    id: int
    path: str

class BulkAddRequest(BaseModel): 
    items: List[SelectedItem]  
    story_id: int
    chapter_id: int	

class StoryCreateSchema(BaseModel): 
	story_name: str

class ChapterCreateSchema(BaseModel): 
    chapter_name: str 
    serial_number: int 
    story_id: int 

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


@router_paragraph.get("/sentences", response_model=dict) 
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

@router_paragraph.delete("/sentences/{id}", status_code=status.HTTP_200_OK) 
async def delete_single_router_paragraph(id: int, session: AsyncSession = Depends(get_db)): 
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

@router_paragraph.post("/sentences/bulk-add", status_code=status.HTTP_200_OK) 
async def bulk_add_storygrid(payload: BulkAddRequest, session: AsyncSession = Depends(get_db)): 
    try: 
        if not payload.items: 
            return {"status": "ignored", "message": "No targets passed."} 

        statement = select(func.max(AudioChapter.serial_number)).where(
            AudioChapter.story_id == payload.story_id,
            AudioChapter.chapter_id == payload.chapter_id
        )

        result = await session.execute(statement)
        max_serial = result.scalar_one_or_none()
        next_serial = (max_serial or 0) + 1
        now = datetime.now(timezone.utc)	 
        inserted_records = []
        for item in payload.items:
            new_audio_chapter = AudioChapter(
                chapter_id=payload.chapter_id,
                story_id=payload.story_id,
                serial_number=next_serial, 
                audio_absolute_filepath=item.path, 
                modified_at=now,
                modified_by="System"
            )
            
            session.add(new_audio_chapter)
            inserted_records.append(new_audio_chapter)
            # Increment tracking sequence number for the next pass
            next_serial += 1
        # 3. Commit batch work to database
        await session.commit()
        # 4. Refresh all inserted objects to populate any database-generated values (like auto-increment IDs)
        for record in inserted_records:
            await session.refresh(record)
        # 5. FIXED: Safely return the populated array back to JavaScript code
        return {
            "status": "success", 
            "message": f"Successfully inserted {len(inserted_records)} items.",
            "data": [record.model_dump() for record in inserted_records] # Converts SQLModel to clean JSON list
        }
    except Exception as e: 
        await session.rollback() 
        print("=== BULK INSERTION EXCEPTION STACK ===") 
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router_paragraph.delete("/sentences/bulk-remove/{item_id}", status_code=status.HTTP_200_OK)
async def delete_audio_chapter(item_id: int, session: AsyncSession = Depends(get_db)):
    try:
        # Query the record by its unique database ID
        statement = select(AudioChapter).where(AudioChapter.id == item_id)
        result = await session.execute(statement)
        record = result.scalar_one_or_none()
        # If the record doesn't exist, return a 404 error
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Audio record with ID {item_id} not found."
            )
        # Remove the record and commit the changes asynchronously
        session.delete(record)
        await session.commit()
        return {"status": "success", "message": f"Record {item_id} deleted successfully."}
    except HTTPException as he:
        raise he
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Database error: {str(e)}"
        )

# ============================================================== 
# STORIES & CHAPTERS ENDPOINTS 
# ============================================================== 
@router_paragraph.post("/stories") 
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

@router_paragraph.post("/chapters") 
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

@router_paragraph.get("/sentences/audio-chapters", status_code=200)
async def get_all_audio_chapters(session: AsyncSession = Depends(get_db)):
    # Fetch all records from the audio_chapters table
    statement = select(AudioChapter)
    result = await session.execute(statement)
    records = result.scalars().all()
    # Return them as a clean list of dictionaries
    return [record.model_dump() for record in records]