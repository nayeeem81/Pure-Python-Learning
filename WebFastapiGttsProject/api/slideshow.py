# api/slideshow.py
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
from io import BytesIO
from datetime import datetime, timezone 
from pydub import AudioSegment

slideshow_router = APIRouter(prefix="/slideshow", tags=["media"])

media_config = {
    "image_folder": "",
    "mp3_file_path": ""
}

VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

class ConfigSchema(BaseModel):
    image_folder: str
    mp3_file_path: str

@slideshow_router.post("/config")
async def update_config(config: ConfigSchema):
    """Updates the active local paths used by the system."""
    # Optional Validation: Check if paths exist on the server machine
    if config.image_folder and not os.path.exists(config.image_folder):
        raise HTTPException(status_code=400, detail="Provided image folder path does not exist")
    if config.mp3_file_path and not os.path.exists(config.mp3_file_path):
        raise HTTPException(status_code=400, detail="Provided MP3 file path does not exist")

    media_config["image_folder"] = config.image_folder
    media_config["mp3_file_path"] = config.mp3_file_path
    return {"status": "success", "config": media_config}

@slideshow_router.get("/config")
async def get_config():
    """Returns the current path configurations."""
    return media_config

@slideshow_router.get("/images")
async def get_images():
    folder = media_config["image_folder"]
    if not folder or not os.path.exists(folder):
        return {"images": [], "message": "No valid folder path configured yet."}
        
    images = [f for f in os.listdir(folder) if f.lower().endswith(VALID_EXTENSIONS)]
    return {"images": images}

@slideshow_router.get("/images/{filename}")
async def serve_image(filename: str):
    folder = media_config["image_folder"]
    if not folder:
        raise HTTPException(status_code=400, detail="Folder path not set")
        
    file_path = os.path.join(folder, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)

@slideshow_router.get("/audio")
async def serve_audio():
    mp3_path = media_config["mp3_file_path"]
    if not mp3_path or not os.path.exists(mp3_path):
        raise HTTPException(status_code=404, detail="Audio file path not set or invalid")
    return FileResponse(mp3_path, media_type="audio/mpeg")

