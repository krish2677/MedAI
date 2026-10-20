import base64
import io
import logging
from PIL import Image, ImageFile

logger = logging.getLogger(__name__)

# ── Limits ─────────────────────────────────────────────────────────────────────
MAX_IMAGE_SIZE   = 10 * 1024 * 1024   # 10 MB file size
MAX_IMAGE_PIXELS = 89_478_485          # ~8000×8000 — PIL default decompression bomb limit
MAX_IMAGE_DIM    = 8000                # max width or height in pixels

# Disable PIL decompression-bomb warning (we enforce our own limits below)
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS
# Never open truncated images silently
ImageFile.LOAD_TRUNCATED_IMAGES = False


def load_image_from_bytes(image_bytes: bytes) -> Image.Image:
    """
    Load a PIL Image from raw bytes with hardened decompression-bomb protection.

    Raises ValueError for:
    - Corrupt or non-image files
    - Images exceeding MAX_IMAGE_PIXELS or MAX_IMAGE_DIM
    """
    try:
        # Open without fully decoding — just read header
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()   # Raises if the file is corrupt / invalid
    except Exception as e:
        raise ValueError(f"Invalid or corrupt image file: {e}")

    # Re-open after verify (PIL file pointer is consumed after verify)
    try:
        img = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        raise ValueError(f"Could not re-open image after verification: {e}")

    # Dimension bomb guard — check before decoding pixels
    w, h = img.size
    if w > MAX_IMAGE_DIM or h > MAX_IMAGE_DIM:
        raise ValueError(
            f"Image dimensions ({w}×{h}) exceed the allowed maximum of "
            f"{MAX_IMAGE_DIM}×{MAX_IMAGE_DIM} pixels."
        )
    if w * h > MAX_IMAGE_PIXELS:
        raise ValueError(
            f"Image pixel count ({w * h:,}) exceeds the safe limit "
            f"of {MAX_IMAGE_PIXELS:,} pixels."
        )

    return img


def preprocess_image(image: Image.Image, target_size: tuple = (380, 380)) -> Image.Image:
    """Convert image to RGB and resize to target dimensions."""
    if image.mode != "RGB":
        image = image.convert("RGB")
    return image.resize(target_size, Image.LANCZOS)


def image_to_base64(image: Image.Image, fmt: str = "PNG") -> str:
    """Convert a PIL Image to a base64-encoded string."""
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def base64_to_image(b64_string: str) -> Image.Image:
    """Decode a base64 string back into a PIL Image."""
    try:
        image_bytes = base64.b64decode(b64_string)
    except Exception as e:
        raise ValueError(f"Invalid base64 string: {e}")
    return Image.open(io.BytesIO(image_bytes))


def validate_image_size(image_bytes: bytes, max_bytes: int = MAX_IMAGE_SIZE) -> bool:
    """Return True if image is within the allowed size limit."""
    return len(image_bytes) <= max_bytes
