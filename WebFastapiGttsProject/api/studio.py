from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from studio_utility.processor import mix_audio_layers

class MixRequest(BaseModel):
    layer_one: str
    layer_two: str

studio_router = APIRouter(prefix="/studio", tags=["Studio Engineering"])

@studio_router.post("/mix")
def handle_audio_mixing(data: MixRequest):
    try:
        result = mix_audio_layers(data.layer_one, data.layer_two)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def iterfile():
	with open(file_path, mode="rb") as file_like:
		yield from file_like
		# Stream the file chunk by chunk so it loads instantly in the player
		return StreamingResponse(iterfile(), media_type="audio/wav")
