# api/textipyimage.py
# 1. Standard Library Imports
from datetime import datetime, timezone
import os
from pathlib import Path

# 2. Third-Party Imports
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Session, select						
# 3. Local Application Imports
from data.database import get_db
from data.model import ImageMetadata
from utilities.image_processing import load_rgb_tensor, tensor_payload, composite_text_on_image

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


# 1. Pydantic schema matching the JSON request payload from your JS event handler
class BakeTextRequest(BaseModel):
    title: str
    short_brief: str

# Resolve the absolute path to the project root static folder
# Path(__file__).resolve()   -> .../WebFastapiGttsProject/api/magiclens.py
# .parent.parent            -> .../WebFastapiGttsProject (Project Root)
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

@router_textipyimage.get("/current", response_model=ImageMetadataResponse | None, status_code=status.HTTP_200_OK)
async def get_image_metadata(session: Session = Depends(get_db)):
    """Retrieve the current image metadata."""
    try:
        statement = select(ImageMetadata)
        result = await session.execute(statement)
        metadata = result.scalars().first()

        if not metadata:
            return None

        return ImageMetadataResponse(
            id=metadata.id,
            title=metadata.title,
            short_brief=metadata.short_brief,
            version=metadata.version,
            modified_at=metadata.modified_at
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metadata retrieval failed: {str(exc)}"
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

@router_textipyimage.get("/tensor")
async def get_image_tensor():
    """Retrieve the current image tensor."""
    try:
        payload = tensor_payload(load_rgb_tensor(DEFAULT_IMAGE))
        return JSONResponse(content=payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tensor payload mapping failure: {str(exc)}"
        )

@router_textipyimage.get("/download-baked")
async def download_baked_image(session: Session = Depends(get_db)):
    # 1. Grab the latest metadata string entries from PostgreSQL
    statement = select(ImageMetadata)
    result = await session.execute(statement)
    metadata = result.scalars().first()
    
    # 2. Load your raw base matrix tensor
    raw_image_matrix = load_rgb_tensor() 
    
    # 3. 🚀 BAKING IT ON THE BACKEND: Pass text straight to your utility
    if metadata:
        final_matrix = composite_text_on_image(
            image_array=raw_image_matrix,
            title=metadata.title,
            short_brief=metadata.short_brief
        )
    else:
        final_matrix = raw_image_matrix

    # 4. Stream the raw baked array cleanly back to the web browser
    buffer = io.BytesIO()
    Image.fromarray(final_matrix).save(buffer, format="PNG")
    buffer.seek(0)
    
    return StreamingResponse(buffer, media_type="image/png")


# 2. The core endpoint handling your JavaScript Apply button network requests
@router_textipyimage.post("/bake-text", status_code=status.HTTP_200_OK)
async def bake_text_to_tensor(request: BakeTextRequest):
    """
    Accept text inputs, composite them into the raw image pixels via NumPy/PIL,
    and return the updated H x W x 3 tensor structure.
    """
    try:
        # A. Load your raw system base matrix data tensor
        # (Falls back onto your custom default gradient sample.png if missing)
        raw_image_matrix = load_rgb_tensor()
        
        # B. 🎨 BACKEND PIXEL BAKING: Permanently merge the strings onto the pixel matrix arrays
        baked_image_matrix = composite_text_on_image(
            image_array=raw_image_matrix,
            title=request.title,
            short_brief=request.short_brief
        )
        
        # C. Transform the raw processed NumPy matrix data into JSON-friendly formats for JS layers
        payload = tensor_payload(baked_image_matrix)
        return payload

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tensor compositing engine failed: {str(exc)}"
        )

