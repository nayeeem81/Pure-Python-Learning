# api/magiclens.py

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
from utilities.image_processing import load_rgb_tensor, tensor_payload

# Initialize a dedicated router for tensor operations
router_magiclens = APIRouter(tags=["Image Tensor/Numpy Engine"])

# Resolve the absolute path to the project root static folder
# Path(__file__).resolve()   -> .../WebFastapiGttsProject/api/magiclens.py
# .parent.parent            -> .../WebFastapiGttsProject (Project Root)
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_IMAGE = BASE_DIR / "static" / "sample.png"


@router_magiclens.get("/tensor")
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
