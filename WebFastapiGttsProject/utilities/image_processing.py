# utilities/image_processing.py
from pathlib import Path
import io
import base64
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
from textwrap import wrap

# Resolve the absolute path to the project root static folder
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_IMAGE = BASE_DIR / "static" / "sample.png"


def get_system_font(size: int = 40):
    """Return a system font with fallback to default."""
    # Try to load a common system font; fallback to default
    font_paths = [
        "/Windows/Fonts/arial.ttf",  # Windows
        "/System/Library/Fonts/Arial.ttf",  # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
    ]
    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            continue
    # Fallback to default font
    return ImageFont.load_default()


def composite_text_on_image(
    image_array: np.ndarray,
    title: str,
    short_brief: str,
    bg_color=(20, 20, 20),
    text_color=(255, 255, 255),
    accent_color=(245, 196, 81)
) -> np.ndarray:
    """
    Composite title and short brief text onto an image in presentation style.
    Places text in optimal positions based on image dimensions.

    Args:
        image_array: H x W x 3 uint8 RGB matrix
        title: Title text (usually short)
        short_brief: Brief description (usually longer)
        bg_color: Background color for text overlays (RGB tuple)
        text_color: Primary text color (RGB tuple)
        accent_color: Accent color for title (RGB tuple)

    Returns:
        H x W x 3 uint8 RGB matrix with text composited
    """
    # Clone array to avoid modifying the original
    result = image_array.copy()
    img = Image.fromarray(result, mode="RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    height, width = result.shape[:2]

    # Calculate safe margins
    margin_x = max(20, width // 20)
    margin_y = max(20, height // 20)

    # Determine font sizes based on image dimensions
    title_font_size = max(24, int(height / 12))
    brief_font_size = max(16, int(height / 18))

    title_font = get_system_font(title_font_size)
    brief_font = get_system_font(brief_font_size)

    # Calculate usable width for text
    usable_width = width - (2 * margin_x)

    y_position = margin_y

    # Draw Title (top-left, accent color with semi-transparent background)
    if title:
        title_lines = wrap(title, width=max(15, usable_width // (title_font_size // 2)))

        for line in title_lines:
            # Get bounding box for text
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Add semi-transparent background box
            padding = 8
            bg_box = [
                margin_x - padding,
                y_position - padding,
                margin_x + text_width + padding,
                y_position + text_height + padding,
            ]
            draw.rectangle(bg_box, fill=(*bg_color, 200), outline=accent_color)

            # Draw text
            draw.text((margin_x, y_position), line, fill=text_color, font=title_font)

            y_position += text_height + 12

        y_position += 20  # Add spacing after title

    # Draw Short Brief (below title, left-aligned with semi-transparent background)
    if short_brief:
        brief_lines = wrap(short_brief, width=max(20, usable_width // (brief_font_size // 2)))

        # Merge all brief lines and create background box
        brief_text_height = 0
        for line in brief_lines:
            bbox = draw.textbbox((0, 0), line, font=brief_font)
            brief_text_height += (bbox[3] - bbox[1]) + 6

        # Draw background box for brief
        padding = 8
        bg_box = [
            margin_x - padding,
            y_position - padding,
            margin_x + usable_width + padding,
            y_position + brief_text_height + padding,
        ]
        draw.rectangle(bg_box, fill=(*bg_color, 180))

        # Draw brief text
        for line in brief_lines:
            draw.text((margin_x, y_position), line, fill=text_color, font=brief_font)

            bbox = draw.textbbox((0, 0), line, font=brief_font)
            y_position += (bbox[3] - bbox[1]) + 6

    # Convert back to array
    return np.asarray(img, dtype=np.uint8)


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
