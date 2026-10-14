# Main API routing file (or a routes/ directory)
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from gtts import gTTS
import io
# Absolute import from your root utility folder
from studio_utility.processor import mix_audio_layers

api_router = APIRouter()


class MixRequest(BaseModel):
    layer_one: str
    layer_two: str

@api_router.post("/mix")
def handle_audio_mixing(data: MixRequest):
    try:
        # Pass web-request payloads into your underlying engine
        result = mix_audio_layers(data.layer_one, data.layer_two)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

AUDIO_STORAGE_DIR = "C:/VisualStudioPyProjects/PurePythonApp/audio_files"

@api_router.get("/generate-tts")
async def generate_tts(text: str):
    """Generates NEW live audio in-memory from text."""
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    mp3_fp = io.BytesIO()
    tts = gTTS(text=text, lang='en')
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    
    return StreamingResponse(mp3_fp, media_type="audio/mp3")


@api_router.get("/play-file/{filename}")
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
