import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Label mappings for each modality
# ---------------------------------------------------------------------------

# HAM10000 skin-lesion class names → human-readable condition labels
SKIN_LABEL_MAP = {
    "nv":     "Melanocytic Nevi (Benign Mole)",
    "mel":    "Melanoma",
    "bkl":    "Benign Keratosis",
    "bcc":    "Basal Cell Carcinoma",
    "akiec":  "Actinic Keratosis / Intraepithelial Carcinoma",
    "df":     "Dermatofibroma",
    "vasc":   "Vascular Lesion",
    # handle alternate label formats (full name or index)
    "melanocytic_nevi":              "Melanocytic Nevi (Benign Mole)",
    "melanoma":                      "Melanoma",
    "benign_keratosis-like_lesions": "Benign Keratosis",
    "basal_cell_carcinoma":          "Basal Cell Carcinoma",
    "actinic_keratoses":             "Actinic Keratosis / Intraepithelial Carcinoma",
    "dermatofibroma":                "Dermatofibroma",
    "vascular_lesions":              "Vascular Lesion",
}

# Retinal / eye condition label normalizer (Ken0965 SwinV2 / APTOS / EyePACS / ODIR)
RETINA_LABEL_MAP = {
    # 9-class fundus diseases (Ken0965 SwinV2)
    "diabetic retinopathy":              "Diabetic Retinopathy",
    "diabetic_retinopathy":              "Diabetic Retinopathy",
    "glaucoma":                          "Glaucoma",
    "retinal detachment":                "Retinal Detachment",
    "retinal_detachment":                "Retinal Detachment",
    "disc edema":                        "Disc Edema / Papilledema",
    "disc_edema":                        "Disc Edema / Papilledema",
    "central serous chorioretinopathy":  "Central Serous Chorioretinopathy",
    "macular scar":                      "Macular Scar / Degeneration (AMD)",
    "macular_scar":                      "Macular Scar / Degeneration (AMD)",
    "myopia":                            "Pathological Myopia",
    "retinitis pigmentosa":              "Retinitis Pigmentosa",
    "retinitis_pigmentosa":              "Retinitis Pigmentosa",
    "healthy":                           "Normal / Healthy Retina",
    "cataract":                          "Cataract",
    "normal":                            "Normal / Healthy Retina",
    "others":                            "Other Retinal Finding",
    # DR clinical stage mappings (Aptos / EyePACS)
    "no dr":                             "Normal / Healthy Retina (No DR)",
    "no_dr":                             "Normal / Healthy Retina (No DR)",
    "nodr":                              "Normal / Healthy Retina (No DR)",
    "a_nodr":                            "Normal / Healthy Retina (No DR)",
    "mild":                              "Mild Non-Proliferative Diabetic Retinopathy",
    "milddr":                            "Mild Non-Proliferative Diabetic Retinopathy",
    "b_milddr":                          "Mild Non-Proliferative Diabetic Retinopathy",
    "moderate":                          "Moderate Diabetic Retinopathy",
    "moderatedr":                        "Moderate Diabetic Retinopathy",
    "c_moderatedr":                      "Moderate Diabetic Retinopathy",
    "severe":                            "Severe Diabetic Retinopathy",
    "severedr":                          "Severe Diabetic Retinopathy",
    "d_severedr":                        "Severe Diabetic Retinopathy",
    "proliferative":                     "Proliferative Diabetic Retinopathy",
    "prodr":                             "Proliferative Diabetic Retinopathy",
    "e_prodr":                           "Proliferative Diabetic Retinopathy",
    "proliferative_diabetic_retinopathy":"Proliferative Diabetic Retinopathy",
    "dr":                                "Diabetic Retinopathy",
    "age-related macular degeneration":  "Macular Scar / Degeneration (AMD)",
    "hypertensive retinopathy":          "Hypertensive Retinopathy",
}

# Chest X-Ray multi-disease label normalizer (Swin / ViT / NIH-14)
CHEST_LABEL_MAP = {
    # Swin lungs disease classes
    "corona virus disease":  "COVID-19 (Coronavirus)",
    "coronavirus disease":   "COVID-19 (Coronavirus)",
    "covid":                 "COVID-19 (Coronavirus)",
    "covid_19":              "COVID-19 (Coronavirus)",
    "tuberculosis":          "Tuberculosis (TB)",
    "tb":                    "Tuberculosis (TB)",
    "bacterial pneumonia":   "Bacterial Pneumonia",
    "viral pneumonia":       "Viral Pneumonia",
    "pneumonia":             "Pneumonia",
    "normal":                "Normal / Healthy Lungs",
    "no finding":            "Normal / Healthy Lungs",
    # Additional thoracic pathologies
    "atelectasis":           "Atelectasis",
    "cardiomegaly":          "Cardiomegaly",
    "effusion":              "Pleural Effusion",
    "infiltration":          "Infiltration",
    "mass":                  "Pulmonary Mass",
    "nodule":                "Pulmonary Nodule",
    "pneumothorax":          "Pneumothorax",
    "consolidation":         "Consolidation",
    "edema":                 "Pulmonary Edema",
    "emphysema":             "Emphysema",
    "fibrosis":              "Pulmonary Fibrosis",
    "pleural_thickening":    "Pleural Thickening",
    "hernia":                "Hiatal Hernia",
}

# Zero-shot candidate labels used as fallback (CLIP-style)
CHEST_ZERO_SHOT_LABELS = [
    "covid-19 pneumonia chest x-ray", "tuberculosis chest x-ray", "bacterial pneumonia",
    "viral pneumonia", "normal healthy chest x-ray", "cardiomegaly enlarged heart",
    "pleural effusion fluid", "pneumothorax collapsed lung", "pulmonary edema",
    "pulmonary fibrosis", "emphysema",
]

SKIN_ZERO_SHOT_LABELS = [
    "melanoma skin cancer", "benign mole", "basal cell carcinoma",
    "actinic keratosis", "dermatofibroma", "benign keratosis", "vascular skin lesion",
]

RETINA_ZERO_SHOT_LABELS = [
    "diabetic retinopathy fundus image",
    "proliferative diabetic retinopathy",
    "normal healthy retina fundus scan",
    "glaucoma optic nerve damage",
    "cataract clouded eye lens",
    "macular degeneration retinal scan",
    "hypertensive retinopathy",
]


def _normalize_label(raw_label: str, label_map: dict) -> str:
    """Attempt to map a raw model label to a human-readable condition name."""
    key = raw_label.lower().strip().replace("-", "_").replace(" ", "_")
    # exact match first
    if key in label_map:
        return label_map[key]
    # original lower
    key2 = raw_label.lower().strip()
    if key2 in label_map:
        return label_map[key2]
    # partial match
    for map_key, value in label_map.items():
        if map_key in key2 or key2 in map_key:
            return value
    # return title-cased raw label as fallback
    return raw_label.replace("_", " ").title()


class CVModel:
    """
    Multimodal Medical Vision Model supporting three imaging modalities:
      - chest_xray  : Chest X-Ray (Pneumonia + 14 NIH pathologies)
      - skin        : Skin Lesion / Dermatology (HAM10000 7-class)
      - retina      : Retinal / Fundus scan (Glaucoma, DR, and other eye diseases)

    Each modality loads its own fine-tuned HuggingFace ViT pipeline.
    Falls back to zero-shot CLIP when specialist is unavailable.
    """

    def __init__(self, weights_path: str = None, modality: str = "chest_xray"):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.modality = modality
        self._is_loaded = False
        self.specialist_pipeline = None
        self._pipeline_type = "image-classification"  # or "zero-shot-image-classification"

        logger.info(f"Loading CV model for modality: {modality}")

        if modality == "chest_xray":
            self._load_chest_model()
        elif modality == "skin":
            self._load_skin_model()
        elif modality == "retina":
            self._load_retina_model()
        else:
            logger.error(f"Unknown modality '{modality}'. Defaulting to chest_xray.")
            self._load_chest_model()

    # ------------------------------------------------------------------
    # Loader helpers
    # ------------------------------------------------------------------

    def _load_chest_model(self):
        """Load multi-disease Chest X-Ray specialist (COVID-19, Tuberculosis, Bacterial/Viral Pneumonia, Normal)."""
        # Primary: Multi-class Swin Transformer fine-tuned on COVID, TB, Bacterial/Viral Pneumonia & Normal
        for model_id in [
            "gianlab/swin-tiny-patch4-window7-224-finetuned-lungs-disease",
            "luciana/swin-tiny-patch4-window7-224-finetuned-lungs-disease",
            "nickmuchi/vit-finetuned-chest-xray-pneumonia",
            "codewithdark/vit-chest-xray",
        ]:
            try:
                from transformers import pipeline as hf_pipeline
                self.specialist_pipeline = hf_pipeline(
                    "image-classification",
                    model=model_id,
                    device=self.device,
                )
                self._pipeline_type = "image-classification"
                self._is_loaded = True
                logger.info(f"✅ Chest X-Ray model loaded: {model_id}")
                return
            except Exception as e:
                logger.warning(f"Could not load {model_id}: {e}")

        self._load_zero_shot_fallback(CHEST_ZERO_SHOT_LABELS)

    def _load_skin_model(self):
        """Load fine-tuned Skin Lesion specialist (HAM10000). Priority given to lightweight models (<50MB)."""
        for model_id in [
            "Anwarkh1/Skin_Cancer-Image_Classification",
            "nickmuchi/skin-cancer-detection-efficientnet",
            "Kuldeepmishra3/vit-large-skin-cancer-ham10000",
        ]:
            try:
                from transformers import pipeline as hf_pipeline
                self.specialist_pipeline = hf_pipeline(
                    "image-classification",
                    model=model_id,
                    device=self.device,
                )
                self._pipeline_type = "image-classification"
                self._is_loaded = True
                logger.info(f"✅ Skin Lesion model loaded: {model_id}")
                return
            except Exception as e:
                logger.warning(f"Could not load {model_id}: {e}")

        self._load_zero_shot_fallback(SKIN_ZERO_SHOT_LABELS)

    def _load_retina_model(self):
        """Load comprehensive multi-disease Retinal specialist (Diabetic Retinopathy, Glaucoma, AMD, etc.)."""
        # Primary: Ken0965 SwinV2 9-class fundus classifier (~110MB)
        try:
            from transformers import pipeline as hf_pipeline, AutoImageProcessor, AutoModelForImageClassification
            proc = AutoImageProcessor.from_pretrained("microsoft/swinv2-tiny-patch4-window8-256")
            model = AutoModelForImageClassification.from_pretrained("Ken0965/eye_fundus_swinV2_tiny_ViT_model")
            self.specialist_pipeline = hf_pipeline(
                "image-classification",
                model=model,
                image_processor=proc,
                device=self.device,
            )
            self._pipeline_type = "image-classification"
            self._is_loaded = True
            logger.info("✅ Multi-disease Retina SwinV2 model loaded: Ken0965/eye_fundus_swinV2_tiny_ViT_model")
            return
        except Exception as e:
            logger.warning(f"Could not load primary SwinV2 eye model ({e}). Trying fallback...")

        # Fallback to rafalosa or ttangmo24
        for model_id in [
            "rafalosa/diabetic-retinopathy-224-procnorm-vit",
            "ttangmo24/vit-base-classification-Eye-Diseases-New02",
        ]:
            try:
                from transformers import pipeline as hf_pipeline
                self.specialist_pipeline = hf_pipeline(
                    "image-classification",
                    model=model_id,
                    device=self.device,
                )
                self._pipeline_type = "image-classification"
                self._is_loaded = True
                logger.info(f"✅ Retina fallback model loaded: {model_id}")
                return
            except Exception as e:
                logger.warning(f"Could not load {model_id}: {e}")

        # If fine-tuned specialists fail, fall back to CLIP zero-shot with clinical retinal labels (NEVER ImageNet!)
        self._load_zero_shot_fallback(RETINA_ZERO_SHOT_LABELS)

    def _load_zero_shot_fallback(self, candidate_labels: list):
        """Fallback: use CLIP zero-shot image classification."""
        try:
            from transformers import pipeline as hf_pipeline
            self.specialist_pipeline = hf_pipeline(
                "zero-shot-image-classification",
                model="openai/clip-vit-base-patch32",
                device=self.device,
            )
            self._candidate_labels = candidate_labels
            self._pipeline_type = "zero-shot-image-classification"
            self._is_loaded = True
            logger.info("✅ Fallback CLIP zero-shot pipeline loaded.")
        except Exception as e:
            logger.error(f"FATAL: All vision models failed to load: {e}")
            self._is_loaded = False

    # ------------------------------------------------------------------
    # Label map per modality
    # ------------------------------------------------------------------

    def _get_label_map(self) -> dict:
        if self.modality == "skin":
            return SKIN_LABEL_MAP
        elif self.modality == "retina":
            return RETINA_LABEL_MAP
        else:
            return CHEST_LABEL_MAP

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict(self, image: Image.Image) -> list:
        if not self._is_loaded or self.specialist_pipeline is None:
            return [{"condition": "Vision Model Offline", "confidence": 0.0, "source": "image_model"}]

        if image.mode != "RGB":
            image = image.convert("RGB")

        label_map = self._get_label_map()

        try:
            # --- Run inference ---
            if self._pipeline_type == "zero-shot-image-classification":
                raw = self.specialist_pipeline(image, candidate_labels=self._candidate_labels)
            else:
                raw = self.specialist_pipeline(image)

            logger.info(f"[{self.modality}] Raw model output: {raw}")

            # Normalise labels and build result list
            results = []
            for item in raw:
                raw_label = str(item.get("label", "Unknown"))
                score = float(item.get("score", 0.0))
                human_label = _normalize_label(raw_label, label_map)
                results.append({
                    "condition": human_label,
                    "confidence": round(score, 4),
                    "source": "image_model",
                })

            # Check secondary Cataract pipeline for retinal modality (threshold > 0.60 to avoid false positives on fundus images)
            if self.modality == "retina" and getattr(self, "cataract_pipeline", None) is not None:
                try:
                    cat_raw = self.cataract_pipeline(image)
                    for item in cat_raw:
                        lbl = str(item.get("label", "")).lower().strip()
                        sc = round(float(item.get("score", 0.0)), 4)
                        if lbl == "cataract" and sc > 0.60:
                            results.append({
                                "condition": "Cataract",
                                "confidence": sc,
                                "source": "image_model",
                            })
                except Exception as cat_e:
                    logger.warning(f"Secondary cataract inference error: {cat_e}")

            # Deduplicate by condition taking maximum confidence
            dedup = {}
            for r in results:
                cond = r["condition"]
                if cond not in dedup or r["confidence"] > dedup[cond]["confidence"]:
                    dedup[cond] = r
            results = list(dedup.values())

            # Sort descending and cap at top-5
            results.sort(key=lambda x: x["confidence"], reverse=True)
            return results[:5]

        except Exception as e:
            logger.error(f"[{self.modality}] Image prediction failed: {e}", exc_info=True)
            return [{"condition": "Prediction Error", "confidence": 0.0, "source": "image_model"}]

    # ------------------------------------------------------------------
    # Grad-CAM stub (returns random tensor — real Grad-CAM hook is in gradcam/)
    # ------------------------------------------------------------------

    def get_tensor_for_gradcam(self, image: Image.Image) -> torch.Tensor:
        return torch.randn(1, 3, 224, 224)

    @property
    def is_loaded(self) -> bool:
        return getattr(self, "_is_loaded", False)
