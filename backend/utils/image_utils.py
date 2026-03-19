import base64
import io
import logging
from PIL import Image

logger = logging.getLogger(__name__)

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB


def load_image_from_bytes(image_bytes: bytes) -> Image.Image:
    """Load a PIL Image from raw bytes."""
    try:
        return Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        raise ValueError(f"Could not load image: {e}")


def preprocess_image(image: Image.Image, target_size: tuple = (380, 380)) -> Image.Image:
    """Convert image to RGB and resize to target dimensions."""
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")
    elif image.mode == "L":
        image = image.convert("RGB")
    return image.resize(target_size, Image.LANCZOS)


def image_to_base64(image: Image.Image, fmt: str = "PNG") -> str:
    """Convert a PIL Image to a base64-encoded string."""
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def base64_to_image(b64_string: str) -> Image.Image:
    """Decode a base64 string back into a PIL Image."""
    image_bytes = base64.b64decode(b64_string)
    return Image.open(io.BytesIO(image_bytes))


def validate_image_size(image_bytes: bytes, max_bytes: int = MAX_IMAGE_SIZE) -> bool:
    """Return True if image is within the allowed size limit."""
    return len(image_bytes) <= max_bytes
