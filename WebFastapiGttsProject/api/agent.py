# api/agent.py
import os
import io
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, StreamingResponse
from gtts import gTTS
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Database dependencies and ORM Models
from data.database import get_db
from data.model import Sentence, Word, Story, Chapter

agent_router = APIRouter(prefix="/agent", tags=["Agent Operations"])

# api/agent.py
import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from gtts import gTTS

agent_router = APIRouter(prefix="/agent", tags=["Agent Operations"])

BASE_DIR = Path(__file__).resolve().parent.parent

AUDIO_DIR = BASE_DIR / "audio_files"

os.makedirs(AUDIO_DIR, exist_ok=True)

@agent_router.get("/generate-tts")
async def generate_tts(text: str):
    """
    💡 FIX 4: Pure, high-speed text-to-speech media streaming engine block.
    Removes database read locks to completely prevent transaction deadlocks.
    """
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    try:
        mp3_fp = io.BytesIO()
        tts = gTTS(text=text, lang='en')
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        return StreamingResponse(mp3_fp, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio runtime stream processing failure: {str(e)}")


@agent_router.get("/play-file/{filename}")
async def play_audio_file(filename: str):
    file_path = AUDIO_DIR / filename
    # Debug print: This will print out exactly WHERE the server is looking in your terminal!
    print(f"DEBUG: Looking for file at -> {file_path.resolve()}")
    
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File missing on disk")
        
    # Make sure your media_type matches the file extension (.wav or .mp3)
    media_type = "audio/mpeg" if filename.endswith(".mp3") else "audio/wav"
    return FileResponse(path=file_path, media_type=media_type)


@agent_router.get("/generate-tts")
async def generate_tts(text: str, db: AsyncSession = Depends(get_db)):
    """
    Generates NEW live audio in-memory from text, streams it immediately 
    to the HTML audio player, and saves the text baseline inside the database.
    """
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    try:
        # 1. Compile audio stream data entirely in-memory
        mp3_fp = io.BytesIO()
        tts = gTTS(text=text, lang='en')
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        raw_audio_bytes = mp3_fp.getvalue() # Extract raw byte stream array

        # 2. 💡 OPTIONAL DB SYNC: Check if this sentence text context already exists
        stmt = select(Sentence).where(Sentence.text_content == text)
        res = await db.execute(stmt)
        existing_sentence = res.scalar_one_or_none()

        if not existing_sentence:
            # Save a baseline entry so the application registers the user's input text immediately
            new_sentence = Sentence(
                text_content=text,
                audio_bytes=raw_audio_bytes, # Cache raw voice bytes directly to PostgreSQL
                mp3_file_path=None,
                original_sentence_json=None,
                modified_sentence_json=None
            )
            db.add(new_sentence)
            # The transaction automatically flushes and commits when the route returns
            print(f"📄 Cached new audio stream template for text: '{text[:20]}...'")
        else:
            print(f"📄 Sentence text match found in DB cache. Streaming live audio out.")

        # 3. Stream the file data directly back to the HTML audio player element
        return StreamingResponse(io.BytesIO(raw_audio_bytes), media_type="audio/mp3")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio generation pipeline error: {str(e)}")
