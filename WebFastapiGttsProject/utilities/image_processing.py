# utilities/image_processing.py
from pathlib import Path
import io
import base64
from PIL import Image
import numpy as np

# Resolve the absolute path to the project root static folder
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_IMAGE = BASE_DIR / "static" / "sample.png"

def get_image_data_url(image_array: np.ndarray) -> str:
    """
    Converts a standard image array/tensor into a base64 encoded data URI.
    Replaces torch.clamp and byte operations with pure NumPy operations.
    """
    clamped = np.clip(image_array, 0, 1)
    scaled = (clamped * 255).astype(np.uint8)
    
    # If the layout is channels-first (3, H, W), transpose it to channels-last (H, W, 3)
    if scaled.ndim == 3 and scaled.shape[0] == 3:
        scaled = np.transpose(scaled, (1, 2, 0))

    output = io.BytesIO()
    Image.fromarray(scaled, mode="RGB").save(output, format="PNG")
    encoded = base64.b64encode(output.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def create_sample_image(path: Path = DEFAULT_IMAGE) -> Path:
    """Create a small RGB test image when no source image has been supplied."""
    path.parent.mkdir(parents=True, exist_ok=True)
    
    height, width = 96, 144
    y, x = np.mgrid[0:height, 0:width]
    red = (x / (width - 1) * 255).astype(np.uint8)
    green = (y / (height - 1) * 255).astype(np.uint8)
    blue = (((x + y) / (width + height - 2)) * 255).astype(np.uint8)
    tensor = np.stack((red, green, blue), axis=-1)
    Image.fromarray(tensor, mode="RGB").save(path)
    return path


def load_rgb_tensor(path: Path = DEFAULT_IMAGE) -> np.ndarray:
    """Load an image as an H x W x 3 uint8 RGB matrix."""
    if not path.exists():
        create_sample_image(path)
    with Image.open(path) as image:
        return np.asarray(image.convert("RGB"), dtype=np.uint8).copy()


def tensor_payload(tensor: np.ndarray) -> dict:
    """Convert the matrix into JSON-friendly data for the canvas layer."""
    height, width, channels = tensor.shape
    if channels != 3:
        raise ValueError("Expected an RGB matrix with three channels")
    return {
        "width": width,
        "height": height,
        "channels": ["r", "g", "b"],
        "pixels": tensor.tolist(),
    }
