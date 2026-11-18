# api/textipyimage.py
# Standard Library Imports
from datetime import datetime, timezone
import os
from pathlib import Path
import uuid
import shutil

# Third-Party Imports
from fastapi import File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status
from starlette.middleware.sessions import SessionMiddleware		

# Third-Party Imports
from pydantic import BaseModel
from sqlmodel import Session, select		

# Local Application Imports
from data.database import get_db
from data.model import ImageMetadata
from utilities.image_processing import load_rgb_tensor, tensor_payload, composite_text_on_image

from config import config
# Initialize a dedicated router for tensor operations
router_textipyimage = APIRouter(tags=["Text Into Image - Tensor/Numpy Engine"])

class ImageMetadataRequest(BaseModel):
    """Request model for saving/updating image metadata."""
    title: str
    short_brief: str

class ImageMetadataResponse(BaseModel):
    """Response model for image metadata retrieval."""
    id: int
    title: str
    short_brief: str
    version: int
    modified_at: datetime

class BakeTextRequest(BaseModel):
    title: str
    short_brief: str

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_IMAGE = BASE_DIR / "static" / "sample.png"

@router_textipyimage.post("/save", response_model=ImageMetadataResponse, status_code=status.HTTP_200_OK)
async def save_image_metadata(request: ImageMetadataRequest, session: Session = Depends(get_db)):
    """Save or update image metadata (title and short brief)."""
    try:
        # Always update/replace the latest metadata (single record approach)
        statement = select(ImageMetadata)
        result = await session.execute(statement)
        metadata = result.scalars().first()
        if metadata:
            # Update existing metadata
            metadata.title = request.title
            metadata.short_brief = request.short_brief
            metadata.version += 1
            metadata.modified_at = datetime.now(timezone.utc)
        else:
            # Create new metadata
            metadata = ImageMetadata(
                title=request.title,
                short_brief=request.short_brief,
                version=1
            )
            session.add(metadata)
        await session.commit()
        await session.refresh(metadata)

        return ImageMetadataResponse(
            id=metadata.id,
            title=metadata.title,
            short_brief=metadata.short_brief,
            version=metadata.version,
            modified_at=metadata.modified_at
        )
    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metadata save failed: {str(exc)}"
        )

@router_textipyimage.post("/clear", status_code=status.HTTP_200_OK)
async def clear_image_metadata(session: Session = Depends(get_db)):
    """Clear all image metadata."""
    try:
        statement = select(ImageMetadata)
        result = await session.execute(statement)
        metadata = result.scalars().first()
        if metadata:
            await session.delete(metadata)
            await session.commit()
        return JSONResponse(
            content={"status": "success", "message": "Metadata cleared."},
            status_code=200
        )
    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metadata clear failed: {str(exc)}"
        )

# 2. The core endpoint handling your JavaScript Apply button network requests
@router_textipyimage.post("/bake-text", status_code=status.HTTP_200_OK)
async def bake_text_to_tensor(request: Request, data: BakeTextRequest):
    """
    Accept text inputs, composite them into the raw image pixels via NumPy/PIL,
    and return the updated H x W x 3 tensor structure.
    """									 
    try:
        filename = request.session.get("user_image")
        if not filename:
            raise HTTPException(status_code=404, detail="No image found in session.")
        file_path = os.path.join(config.STORAGE_ROOT, "imageuploads", filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Image file missing on server.")
		
        raw_image_matrix = load_rgb_tensor(file_path)

        baked_image_matrix = composite_text_on_image(
            image_array=raw_image_matrix,
            title=data.title,
            short_brief=data.short_brief
        )

        payload = tensor_payload(baked_image_matrix)

        return payload
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tensor compositing engine failed: {str(exc)}"
        )

@router_textipyimage.post("/upload-image")
async def upload_image(request: Request, file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(config.STORAGE_ROOT, "imageuploads", unique_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    request.session["user_image"] = unique_filename
    return {
        "message": "Image uploaded and saved to session!",
        "filename": unique_filename
    }


@router_textipyimage.get("/my-session-image")
async def get_session_image(request: Request):
    filename = request.session.get("user_image")
    if not filename:
        raise HTTPException(status_code=404, detail="No image found in session.")
    file_path = os.path.join(config.STORAGE_ROOT, "imageuploads", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image file missing on server.")
    return FileResponse(file_path)