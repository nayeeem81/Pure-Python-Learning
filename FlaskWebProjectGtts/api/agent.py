import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from gtts import gTTS
import io

agent_router = APIRouter(prefix="/agent", tags=["Agent"])

# An example directory where you store your existing WAV/MP3 files
AUDIO_STORAGE_DIR = "C:/VisualStudioPyProjects/PurePythonApp/audio_files"

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


@agent_router.get("/play-file/{filename}")
async def play_existing_file(filename: str):
    """Reads an EXISTING file from your disk and streams it to the browser."""
    file_path = os.path.join(AUDIO_STORAGE_DIR, filename)
    
    # Security check: prevent directory traversal attacks
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found on disk")
        
    def iterfile():
        with open(file_path, mode="rb") as file_like:
            yield from file_like

    # Stream the file chunk by chunk so it loads instantly in the player
    return StreamingResponse(iterfile(), media_type="audio/wav")
