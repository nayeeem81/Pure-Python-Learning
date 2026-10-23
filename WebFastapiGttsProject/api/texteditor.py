# api/texteditor.py
import os
import json
import traceback
from fastapi import APIRouter, HTTPException, Depends, Query 
from sqlmodel import select, func 
from sqlmodel.ext.asyncio.session import AsyncSession
from data.database import get_db 
from data.model import Sentence    

router_texteditor = APIRouter(tags=["Text Edit & DSP"])

WORKSPACE_DIR = os.path.abspath("./project")
GENERATED_DIR = os.path.join(WORKSPACE_DIR, "generated")

router_texteditor = APIRouter(tags=["Text Edit & DSP"])
@router_texteditor.get("/sentences", response_model=dict)
async def get_sentences(
    session: AsyncSession = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, le=100)
): 
    try:
        # 1. Query total record count for UI pagination boundaries
        count_statement = select(func.count()).select_from(Sentence)
        count_result = await session.execute(count_statement)
        total_records = count_result.scalar() or 0

        # 2. Query the requested pagination chunk sorted sequentially by ID
        statement = select(Sentence).order_by(Sentence.id).offset(skip).limit(limit) 
        result = await session.execute(statement) 
        sentences = result.scalars().all()
        
        cleaned_sentences = []
        for s in sentences:
            sentence_dict = s.model_dump()
            
            # Initialization fallback keys
            text_val = "No Text Found"
            mp3_val = ""

            # Check if fields are inside original_sentence_json column
            if hasattr(s, "original_sentence_json") and s.original_sentence_json:
                json_data = s.original_sentence_json
                # Parse JSON safely if saved as a raw string format
                if isinstance(json_data, str):
                    try:
                        json_data = json.loads(json_data)
                    except Exception:
                        json_data = {}
                
                if isinstance(json_data, dict):
                    text_val = json_data.get("original_sentence", text_val)
                    mp3_val = json_data.get("master_mp3_path", mp3_val)

            # Fallback directly to column properties if json checks yield default values
            if text_val == "No Text Found":
                if hasattr(s, "text_content") and s.text_content:
                    text_val = s.text_content
                elif hasattr(s, "original_sentence") and s.original_sentence:
                    text_val = s.original_sentence

            if not mp3_val:
                if hasattr(s, "mp3_file_path") and s.mp3_file_path:
                    mp3_val = s.mp3_file_path

            # Reassign clean metadata keys for the Javascript UI grid parsing
            sentence_dict["text_content"] = text_val
            sentence_dict["master_mp3_path"] = mp3_val

            # STRIP OUT raw binary fields that cause the JSON serialization crash
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