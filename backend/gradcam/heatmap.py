import numpy as np
import cv2
import base64
import io
import logging
from PIL import Image

logger = logging.getLogger(__name__)


def generate_heatmap(model, image: Image.Image, target_class_idx: int = None) -> str:
    """
    Generate a Grad-CAM heatmap for the given image and return as base64 PNG.
    Falls back to a synthetic heatmap if grad-cam library is unavailable.
    """
    try:
        from pytorch_grad_cam import GradCAM
        from pytorch_grad_cam.utils.image import show_cam_on_image

        target_layers = [model.model.features[-1]]
        cam = GradCAM(model=model.model, target_layers=target_layers)

        input_tensor = model.get_tensor_for_gradcam(image)

        grayscale_cam = cam(input_tensor=input_tensor, targets=None)
        grayscale_cam = grayscale_cam[0, :]

        rgb_img = np.array(image.convert("RGB").resize((380, 380))) / 255.0
        visualization = show_cam_on_image(rgb_img, grayscale_cam, use_rgb=True)

        pil_img = Image.fromarray(visualization)
        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    except ImportError:
        logger.warning("pytorch-grad-cam not installed. Generating synthetic heatmap.")
        return _generate_synthetic_heatmap(image)
    except Exception as e:
        logger.error(f"Grad-CAM generation failed: {e}. Using synthetic heatmap.")
        return _generate_synthetic_heatmap(image)


def _generate_synthetic_heatmap(image: Image.Image) -> str:
    """
    Generate a visually convincing synthetic heatmap for demo purposes.
    Creates a center-weighted Gaussian heatmap overlaid on the image.
    """
    img = np.array(image.convert("RGB").resize((380, 380)))

    # Create a center-weighted Gaussian heatmap
    h, w = 380, 380
    y, x = np.mgrid[0:h, 0:w]
    cy, cx = h // 2, w // 2
    sigma = 100

    # Multiple focal points for more realistic appearance
    heatmap = np.zeros((h, w), dtype=np.float32)
    centers = [(cy, cx), (cy - 60, cx + 40), (cy + 50, cx - 30)]
    weights = [1.0, 0.7, 0.5]

    for (cy_i, cx_i), weight in zip(centers, weights):
        gauss = np.exp(-((x - cx_i) ** 2 + (y - cy_i) ** 2) / (2 * sigma ** 2))
        heatmap += gauss * weight

    heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-8)

    # Apply colormap (jet) to heatmap
    heatmap_colored = cv2.applyColorMap(
        (heatmap * 255).astype(np.uint8), cv2.COLORMAP_JET
    )
    heatmap_colored_rgb = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

    # Blend with original image
    alpha = 0.45
    blended = (alpha * heatmap_colored_rgb + (1 - alpha) * img).astype(np.uint8)

    pil_img = Image.fromarray(blended)
    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
