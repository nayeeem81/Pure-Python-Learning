# api/texteditor.py
import os
import json
import traceback
from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel
from sqlmodel import select, func 
from sqlmodel.ext.asyncio.session import AsyncSession
from data.database import get_db 
from data.model import Sentence    

router_texteditor = APIRouter(tags=["Text Edit & DSP"])

WORKSPACE_DIR = os.path.abspath("./project")
GENERATED_DIR = os.path.join(WORKSPACE_DIR, "generated")

@router_texteditor.get("/sentences", response_model=dict)
async def get_sentences(
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

            if text_val == "No Text Found":
                if hasattr(s, "text_content") and s.text_content:
                    text_val = s.text_content
                elif hasattr(s, "original_sentence") and s.original_sentence:
                    text_val = s.original_sentence

            if not mp3_val:
                if hasattr(s, "mp3_file_path") and s.mp3_file_path:
                    mp3_val = s.mp3_file_path

            sentence_dict["text_content"] = text_val
            sentence_dict["master_mp3_path"] = mp3_val

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
        print("\n=== DATABASE ERROR TRACEBACK ===")
        traceback.print_exc()
        print("=================================\n")
        raise HTTPException(status_code=500, detail=f"Database operational crash: {str(e)}")

class BulkDeleteRequest(BaseModel):
    ids: list[int]

@router_texteditor.delete("/sentences/{id}", status_code=status.HTTP_200_OK)
async def delete_single_sentence(id: int, session: AsyncSession = Depends(get_db)):
    try:
        statement = select(Sentence).where(Sentence.id == id)
        result = await session.execute(statement)
        sentence = result.scalars().first()

        if not sentence:
            raise HTTPException(status_code=404, detail=f"Sentence ID {id} not found in database records.")

        paths_to_delete = []
        if hasattr(sentence, "mp3_file_path") and sentence.mp3_file_path:
            paths_to_delete.append(sentence.mp3_file_path)
            
        if hasattr(sentence, "original_sentence_json") and sentence.original_sentence_json:
            json_data = sentence.original_sentence_json
            if isinstance(json_data, str):
                try:
                    json_data = json.loads(json_data)
                except Exception:
                    json_data = {}
            
            if isinstance(json_data, dict):
                if "master_mp3_path" in json_data:
                    paths_to_delete.append(json_data["master_mp3_path"])
                if "words_timeline" in json_data and isinstance(json_data["words_timeline"], list):
                    for word_entry in json_data["words_timeline"]:
                        if isinstance(word_entry, dict) and "segment_file" in word_entry:
                            paths_to_delete.append(word_entry["segment_file"])

        for relative_path in set(paths_to_delete):
            if relative_path and relative_path != "#":
                full_file_path = os.path.normpath(os.path.join(WORKSPACE_DIR, relative_path.replace("generated/", "")))
                if os.path.exists(full_file_path):
                    try:
                        os.remove(full_file_path)
                    except Exception as disk_err:
                        print(f"⚠️ Failed to remove disk asset storage slot: {disk_err}")

        await session.delete(sentence)
        await session.commit()
        return {"status": "success", "message": f"Sentence tracking row {id} and files cleared successfully."}

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        print("\n=== SINGLE DELETION EXCEPTION STACK ===")
        traceback.print_exc()
        print("========================================\n")
        raise HTTPException(status_code=500, detail=f"Internal database deletion failure: {str(e)}")

@router_texteditor.post("/sentences/bulk-delete", status_code=status.HTTP_200_OK)
async def bulk_delete_sentences(payload: BulkDeleteRequest, session: AsyncSession = Depends(get_db)):
    try:
        if not payload.ids:
            return {"status": "ignored", "message": "No targets passed."}

        statement = select(Sentence).where(Sentence.id.in_(payload.ids))
        result = await session.execute(statement)
        sentences_to_clear = result.scalars().all()

        if not sentences_to_clear:
            return {"status": "success", "message": "No records found."}

        paths_to_delete = []
        for sentence in sentences_to_clear:
            if hasattr(sentence, "mp3_file_path") and sentence.mp3_file_path:
                paths_to_delete.append(sentence.mp3_file_path)

            if hasattr(sentence, "original_sentence_json") and sentence.original_sentence_json:
                json_data = sentence.original_sentence_json
                if isinstance(json_data, str):
                    try:
                        json_data = json.loads(json_data)
                    except Exception:
                        json_data = {}
                
                if isinstance(json_data, dict):
                    if "master_mp3_path" in json_data:
                        paths_to_delete.append(json_data["master_mp3_path"])
                    if "words_timeline" in json_data and isinstance(json_data["words_timeline"], list):
                        for word_entry in json_data["words_timeline"]:
                            if isinstance(word_entry, dict) and "segment_file" in word_entry:
                                paths_to_delete.append(word_entry["segment_file"])

        for relative_path in set(paths_to_delete):
            if relative_path and relative_path != "#":
                full_file_path = os.path.normpath(os.path.join(WORKSPACE_DIR, relative_path.replace("generated/", "")))
                if os.path.exists(full_file_path):
                    try:
                        os.remove(full_file_path)
                    except Exception:
                        pass

        for sentence in sentences_to_clear:
            await session.delete(sentence)

        await session.commit()
        return {"status": "success", "message": f"Successfully dropped records."}

    except Exception as e:
        await session.rollback()
        print("\n=== BULK DELETION EXCEPTION STACK ===")
        traceback.print_exc()
        print("======================================\n")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
