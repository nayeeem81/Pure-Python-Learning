# api/studio.py
import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

# Database integration
from data.database import get_db
from data.model import SentenceHistory, WordHistory

class MixRequest(BaseModel):
    layer_one: str  # e.g., "generated/full_sentence.mp3"
    layer_two: str  # e.g., "static/background_music.mp3"
    sentence_id: int | None = None  # Optional linking back to our DB tracking layers

studio_router = APIRouter(prefix="/studio", tags=["Studio Engineering"])

@studio_router.post("/mix")
async def handle_audio_mixing(data: MixRequest, db: AsyncSession = Depends(get_db)):
    """
    Asynchronously accepts file path vectors, executes background computational 
    audio layer mixing, and sets up working streaming handles.
    """
    try:
        # 1. Execute our core mathematical sound mixing processing script
        result = mix_audio_layers(data.layer_one, data.layer_two)
        
        # 2. 💡 OPTIONAL SYSTEM LOG: If a sentence ID is provided, you can automatically
        # archive an index snapshot tracking that an engineer mixed this audio file.
        if data.sentence_id:
            print(f"📄 Audit Log: Sentence ID {data.sentence_id} audio mixed.")
            # Your tracking injections out to history tables would resolve here
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@studio_router.get("/stream-track")
async def stream_studio_track(file_path: str):
    """
    Safely opens a file path locally on the machine server disk and streams 
    it chunk-by-chunk to the user browser player without locking memory.
    """
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested audio track missing on disk.")

    # 💡 FIX: Isolated generator function that yields pure binary blocks
    def iterfile():
        with open(file_path, mode="rb") as file_like:
            while chunk := file_like.read(8192): # Stream in safe 8KB blocks
                yield chunk

    # Determine media type dynamically based on file format
    media_type = "audio/mpeg" if file_path.endswith(".mp3") else "audio/wav"
    
    # Return streaming loop out to caller
    return StreamingResponse(iterfile(), media_type=media_type)


# --- PURE LOGICAL COMPUTATIONAL ENGINE ---
# Keep your audio code isolated from web framework components here
def mix_audio_layers(track_a: str, track_b: str) -> dict:
    """
    Computational mixing logic using data arrays or PyDub mixers goes here.
    """
    # Example logic skeleton:
    # sound_a = AudioSegment.from_file(track_a)
    # sound_b = AudioSegment.from_file(track_b)
    # combined = sound_a.overlay(sound_b)
    # combined.export("final_output.mp3", format="mp3")
    
    return {"status": "mixed", "output_file": "final_output.mp3"}
