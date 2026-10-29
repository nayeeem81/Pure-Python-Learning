# api/slideshow.py
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

slideshow_router = APIRouter(tags=["media"])

media_config = {
    "image_folder": "",
    "mp3_folder_path": ""
}

VALID_IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')
VALID_AUDIO_EXTENSIONS = ('.mp3', '.wav', '.flac', '.ogg', '.m4a')

class ConfigSchema(BaseModel):
    image_folder: str
    mp3_folder_path: str

@slideshow_router.post("/config")
async def update_config(config: ConfigSchema):
    """Updates the active local paths used by the system."""
    # Validation: Check if paths exist and are directories
    if config.image_folder:
        if not os.path.isdir(config.image_folder):
            raise HTTPException(status_code=400, detail="Image folder path must be a valid directory")

    if config.mp3_folder_path:
        if not os.path.isdir(config.mp3_folder_path):
            raise HTTPException(status_code=400, detail="MP3 folder path must be a valid directory")

    media_config["image_folder"] = config.image_folder
    media_config["mp3_folder_path"] = config.mp3_folder_path
    return {"status": "success", "config": media_config}

@slideshow_router.get("/config")
async def get_config():
    """Returns the current path configurations."""
    return media_config

@slideshow_router.get("/images")
async def get_images():
    """Returns list of valid image files from configured folder."""
    folder = media_config["image_folder"]
    if not folder or not os.path.isdir(folder):
        return {"images": [], "message": "No valid folder path configured yet."}

    try:
        images = [f for f in os.listdir(folder) if f.lower().endswith(VALID_IMAGE_EXTENSIONS)]
        return {"images": images}
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Failed to read image folder: {str(err)}")

@slideshow_router.get("/images/{filename}")
async def serve_image(filename: str):
    """Serves individual image file from configured folder."""
    folder = media_config["image_folder"]
    if not folder:
        raise HTTPException(status_code=400, detail="Folder path not set")

    # Security: Use basename to prevent path traversal
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(folder, safe_filename)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)

@slideshow_router.get("/mp3-files")
async def get_mp3_playlist():
    """Returns list of MP3 files from configured folder."""
    folder = media_config["mp3_folder_path"]
    if not folder or not os.path.isdir(folder):
        return {"files": [], "message": "No valid MP3 folder path configured yet."}

    try:
        mp3_files = [f for f in os.listdir(folder) if f.lower().endswith(VALID_AUDIO_EXTENSIONS)]
        return {"files": sorted(mp3_files)}
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Failed to read MP3 folder: {str(err)}")

@slideshow_router.get("/mp3/{filename}")
async def serve_mp3(filename: str):
    """Serves individual MP3 file from configured folder."""
    folder = media_config["mp3_folder_path"]
    if not folder:
        raise HTTPException(status_code=400, detail="MP3 folder path not set")

    # Security: Use basename to prevent path traversal
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(folder, safe_filename)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path, media_type="audio/mpeg")
