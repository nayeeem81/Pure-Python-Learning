# api/imagetensor.py
import os
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from pydantic import BaseModel
from datetime import datetime, timezone
from utilities.image_processing import load_rgb_tensor, tensor_payload
from data.database import get_db
from data.model import ImageMetadata

# Initialize a dedicated router for tensor operations
router_imagetensor = APIRouter(tags=["Image Tensor Engine"])


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

# Resolve the absolute path to the project root static folder
# Path(__file__).resolve()   -> .../WebFastapiGttsProject/api/imagetensor.py
# .parent.parent            -> .../WebFastapiGttsProject (Project Root)
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_IMAGE = BASE_DIR / "static" / "sample.png"


@router_imagetensor.post("/metadata/save", response_model=ImageMetadataResponse, status_code=status.HTTP_200_OK)
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


@router_imagetensor.get("/metadata/current", response_model=ImageMetadataResponse | None, status_code=status.HTTP_200_OK)
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


@router_imagetensor.post("/metadata/clear", status_code=status.HTTP_200_OK)
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



@router_imagetensor.get("/tensor")
async def tensor():
    """Generates and returns JSON-friendly pixel matrices for canvas interfaces."""
    try:
        payload = tensor_payload(load_rgb_tensor(DEFAULT_IMAGE))
        return JSONResponse(content=payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tensor payload mapping failure: {str(exc)}"
        )
