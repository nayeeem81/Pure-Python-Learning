# api/slideshow.py
import os
import urllib.parse
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

slideshow_router = APIRouter(tags=["media"])

# 1. This is a normal Python class to store your values in memory
class ConfigStore:
    image_folder: str = ""
    mp3_file_path: str = ""

# FIX: Instantiate the regular Python class, NOT the Pydantic schema model!
config_db = ConfigStore()

# 2. This is your Pydantic schema used ONLY for incoming request data validation
class ConfigPayload(BaseModel):
    image_folder: str
    mp3_file_path: str

config_db.image_folder  = r"D:\projectSlides\image"  # Added 'r' prefix
config_db.mp3_file_path = r"D:\projectSlides\audio"  # Added 'r' prefix
 

VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

@slideshow_router.get("/getconfig")
async def get_config():
    return {
        "image_folder": config_db.image_folder,
        "mp3_file_path": config_db.mp3_file_path
    }

@slideshow_router.post("/config")
async def save_config(payload: ConfigPayload):
    # Verify that the provided path is an actual existing directory
    if payload.mp3_file_path and not os.path.isdir(payload.mp3_file_path):
        raise HTTPException(status_code=400, detail="The MP3 folder path does not exist.")
        
    config_db.image_folder = payload.image_folder
    config_db.mp3_file_path = payload.mp3_file_path
    return {"status": "success"}


@slideshow_router.get("/images")
async def get_images():
    folder = config_db.image_folder
    
    # 1. Print out the exact path string to the console to verify what Python sees
    print(f"DEBUG -> Image folder path read: {repr(folder)}")
    
    # 2. Return an empty fallback array instead of crashing if path layout is missing
    if not folder or not os.path.isdir(folder):
        print(f"DEBUG -> Path is not a valid directory: {folder}")
        return {"images": []}
        
    try:
        # 3. Clean up the folder path structure
        normalized_folder = os.path.normpath(folder)
        
        # 4. Filter files safely
        images = [
            f for f in os.listdir(normalized_folder)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) 
            and os.path.isfile(os.path.join(normalized_folder, f))
        ]
        
        print(f"DEBUG -> Found {len(images)} images: {images}")
        return {"images": images}
        
    except Exception as e:
        # This prevents generic 500 errors by printing the exact crash reason to the console log
        print(f"DEBUG EXCEPTION -> Failed to scan image folder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server folder error: {str(e)}")


@slideshow_router.get("/images/{filename}")
async def serve_image(filename: str): # <-- 2. Add request parameter
    folder =   config_db.mp3_file_path
    if not folder:
        raise HTTPException(status_code=400, detail="Folder path not set")
        
    # 3. Clean out any appended query strings (like ?t=12345) from the filename
    clean_filename = filename.split("?")[0]
        
    # 4. Decode '%20' back to spaces and '%28/%29' back to parentheses
    decoded_filename = urllib.parse.unquote(clean_filename)
    
    # 5. Combine path safely
    file_path = os.path.join(folder, decoded_filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Image not found: {decoded_filename}")
        
    return FileResponse(file_path)


# 1. NEW ENDPOINT: Indexes the folder and returns a list of base filenames
@slideshow_router.get("/playlist")
async def get_audio_playlist():
    folder = config_db.mp3_file_path
    if not folder or not os.path.isdir(folder):
        raise HTTPException(status_code=404, detail="Audio directory path config is invalid or unset.")
    
    try:
        # Scan for MP3 items and sort them alphabetically
        mp3_files = sorted([
            file for file in os.listdir(folder)
            if file.lower().endswith(".mp3") and os.path.isfile(os.path.join(folder, file))
        ])
        return {"playlist": mp3_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scan directory: {str(e)}")

# 2. NEW ENDPOINT: Safely streams the requested file from the indexed folder
@slideshow_router.get("/stream")
async def stream_audio_track(file: str):
    folder = config_db.mp3_file_path
    if not folder or not os.path.isdir(folder):
        raise HTTPException(status_code=404, detail="Audio folder is not configured correctly.")
    
    # Securely construct the absolute filepath to prevent directory traversal exploits
    safe_filename = os.path.basename(urllib.parse.unquote(file))
    target_file_path = os.path.join(folder, safe_filename)
    
    if not os.path.exists(target_file_path):
        raise HTTPException(status_code=444, detail="Requested audio track does not exist.")
        
    return FileResponse(target_file_path, media_type="audio/mpeg")