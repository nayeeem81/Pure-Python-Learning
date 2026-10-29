# api/imagetensor.py
import os
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
from utilities.image_processing import load_rgb_tensor, tensor_payload

# Initialize a dedicated router for tensor operations
router_imagetensor = APIRouter(tags=["Image Tensor Engine"])

# Resolve the absolute path to the project root static folder
# Path(__file__).resolve()   -> .../WebFastapiGttsProject/api/imagetensor.py
# .parent.parent            -> .../WebFastapiGttsProject (Project Root)
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_IMAGE = BASE_DIR / "static" / "sample.png"

@router_imagetensor.post("/editimage", status_code=status.HTTP_200_OK)
async def api_edit_image(request: Request):
    """API endpoint explicitly handling standalone image modifications."""
    try:
        data = await request.json() or {}
        # Your JSON payload modification logic can be parsed safely here...
        return JSONResponse(
            content={"status": "success", "message": "Image tensor processing complete."},
            status_code=200
        )
    except Exception as exc:
        return JSONResponse(content={"error": str(exc)}, status_code=400)


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
