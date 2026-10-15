import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from gtts import gTTS
import io

agent_router = APIRouter(prefix="/agent", tags=["Agent Operations"])

# 1. Get the absolute path of the directory main.py lives in
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Force it to target a folder named "audio_files" at the root level
AUDIO_DIR = BASE_DIR / "audio_files"

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
async def generate_tts(text: str):
    """Generates NEW live audio in-memory from text."""
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    mp3_fp = io.BytesIO()
    tts = gTTS(text=text, lang='en')
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    
    return StreamingResponse(mp3_fp, media_type="audio/mp3")


       