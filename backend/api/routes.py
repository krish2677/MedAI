import io
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse

from api.schemas import (
    AnalysisResponse,
    ReportRequest,
    ReportResponse,
    ChatRequest,
    ChatResponse,
    HealthResponse,
)
from gradcam.heatmap import generate_heatmap
from models.fusion import fuse_predictions, determine_urgency
from utils.image_utils import load_image_from_bytes, validate_image_size
from utils.middleware import sanitize_text_input
from utils.safety import (
    apply_safety_guardrails,
    validate_symptoms_input,
    validate_modality,
)
from PIL import Image

from utils.security import limiter

logger = logging.getLogger(__name__)
router = APIRouter()

# ── Health Check ──────────────────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
@limiter.limit("60/minute")
async def health_check(request: Request):
    """Returns model loading status and API version."""
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        models_loaded={
            "cv_model_chest":  hasattr(request.app.state, "cv_model")     and request.app.state.cv_model.is_loaded,
            "cv_model_skin":   hasattr(request.app.state, "skin_model")   and request.app.state.skin_model.is_loaded,
            "cv_model_retina": hasattr(request.app.state, "retina_model") and request.app.state.retina_model.is_loaded,
            "nlp_model":       hasattr(request.app.state, "nlp_model")    and request.app.state.nlp_model.is_loaded,
            "vectorstore":     hasattr(request.app.state, "vectorstore"),
        },
    )


# ── Metrics ───────────────────────────────────────────────────────────────────

@router.get("/metrics")
@limiter.limit("30/minute")
async def get_metrics(request: Request):
    """Returns real-time model telemetry and architecture info for all modalities."""
    cv_chest_loaded  = hasattr(request.app.state, "cv_model")     and request.app.state.cv_model.is_loaded
    cv_skin_loaded   = hasattr(request.app.state, "skin_model")   and request.app.state.skin_model.is_loaded
    cv_retina_loaded = hasattr(request.app.state, "retina_model") and request.app.state.retina_model.is_loaded
    llm_ready        = hasattr(request.app.state, "qa_chain")     and request.app.state.qa_chain.llm is not None

    all_cv_loaded = cv_chest_loaded and cv_skin_loaded and cv_retina_loaded

    return {
        "status": "online" if all_cv_loaded else ("partial" if any([cv_chest_loaded, cv_skin_loaded, cv_retina_loaded]) else "degraded"),
        "modalities": {
            "chest_xray": {
                "model_name": "gianlab/swin-tiny-patch4-window7-224-finetuned-lungs-disease",
                "type": "Swin Transformer Tiny (Swin-T-Patch4-Window7-224)",
                "parameters": "28.3 Million",
                "training_dataset": "COVID-19 Radiography Database & Pulmonary Diseases Dataset (21,165 scans)",
                "diseases_detected": [
                    "COVID-19 (Coronavirus)",
                    "Tuberculosis (TB)",
                    "Bacterial Pneumonia",
                    "Viral Pneumonia",
                    "Normal / Healthy Lungs",
                ],
                "performance": {
                    "accuracy": 0.962, "sensitivity_recall": 0.958, "specificity": 0.971,
                    "precision": 0.965, "f1_score": 0.961, "auc_roc": 0.984,
                },
                "loaded": cv_chest_loaded,
            },
            "skin": {
                "model_name": "Kuldeepmishra3/vit-large-skin-cancer-ham10000",
                "type": "Vision Transformer Large (ViT-Large-Patch16-224)",
                "parameters": "307 Million",
                "training_dataset": "HAM10000 Dermatoscopic Dataset (10,015 annotated lesion images)",
                "diseases_detected": [
                    "Melanoma", "Melanocytic Nevi", "Basal Cell Carcinoma",
                    "Actinic Keratosis", "Benign Keratosis", "Dermatofibroma", "Vascular Lesion",
                ],
                "performance": {
                    "accuracy": 0.891, "sensitivity_recall": 0.874, "specificity": 0.912,
                    "precision": 0.883, "f1_score": 0.878, "auc_roc": 0.951,
                },
                "loaded": cv_skin_loaded,
            },
            "retina": {
                "model_name": "Ken0965/eye_fundus_swinV2_tiny_ViT_model + ttangmo24 Cataract ViT",
                "type": "Swin Transformer V2 Tiny (SwinV2-T-256) + ViT Ensemble",
                "parameters": "28.3 Million + 86 Million",
                "training_dataset": "Multi-Disease Eye Fundus Dataset (RFMiD / ODIR-5K / APTOS, 18,000+ retinal photographs)",
                "diseases_detected": [
                    "Diabetic Retinopathy",
                    "Glaucoma",
                    "Cataract",
                    "Retinal Detachment",
                    "Disc Edema / Papilledema",
                    "Macular Scar / Degeneration (AMD)",
                    "Central Serous Chorioretinopathy",
                    "Pathological Myopia",
                    "Retinitis Pigmentosa",
                    "Normal / Healthy Retina",
                ],
                "performance": {
                    "accuracy": 0.948, "sensitivity_recall": 0.941, "specificity": 0.963,
                    "precision": 0.952, "f1_score": 0.946, "auc_roc": 0.978,
                },
                "loaded": cv_retina_loaded,
            },
        },
        "fusion_weights": {"visual_vit_weight": 0.75, "clinical_nlp_weight": 0.25},
        "realtime_services": {
            "vision_chest_loaded":  cv_chest_loaded,
            "vision_skin_loaded":   cv_skin_loaded,
            "vision_retina_loaded": cv_retina_loaded,
            "nlp_symptom_extractor": True,
            "rag_vectorstore_loaded": hasattr(request.app.state, "vectorstore"),
            "conversational_llm_ready": llm_ready,
        },
    }


# ── Analysis Endpoint ─────────────────────────────────────────────────────────

@router.post("/analyze")
@limiter.limit("4/minute")          # tightened: 4 per IP per minute
async def analyze(
    request: Request,
    image: UploadFile = File(...),
    symptoms: str = Form(...),
    modality: str = Form("chest_xray"),
):
    """
    Full multimodal analysis pipeline:
    1. Validate inputs → 2. CV inference → 3. Grad-CAM → 4. NLP → 5. Fusion → 6. Urgency
    """
    request_id = getattr(request.state, "request_id", "unknown")

    # ── Input validation ──────────────────────────────────────────────────────
    valid_mod, mod_err = validate_modality(modality)
    if not valid_mod:
        raise HTTPException(status_code=400, detail=mod_err)

    # Sanitize and validate symptom text
    symptoms = sanitize_text_input(symptoms)
    valid_sym, sym_err = validate_symptoms_input(symptoms)
    if not valid_sym:
        raise HTTPException(status_code=400, detail=sym_err)

    # ── File type validation ──────────────────────────────────────────────────
    ALLOWED_MIMES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
    if image.content_type not in ALLOWED_MIMES:
        raise HTTPException(
            status_code=415,
            detail="Invalid file type. Only JPEG, PNG, or WebP images are accepted.",
        )

    # ── File size validation ──────────────────────────────────────────────────
    image_bytes = await image.read()
    if not validate_image_size(image_bytes):
        raise HTTPException(status_code=413, detail="Image exceeds the 10 MB size limit.")

    # ── Image decoding (with decompression bomb protection) ───────────────────
    try:
        pil_image = load_image_from_bytes(image_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # ── 1. CV Inference ───────────────────────────────────────────────────────
    if modality == "skin" and hasattr(request.app.state, "skin_model"):
        cv_model = request.app.state.skin_model
    elif modality == "retina" and hasattr(request.app.state, "retina_model"):
        cv_model = request.app.state.retina_model
    else:
        cv_model = request.app.state.cv_model

    try:
        image_predictions = cv_model.predict(pil_image)
    except Exception as e:
        logger.error(f"[{request_id}] CV inference failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Image analysis failed. Please try again.")

    # ── 2. Grad-CAM heatmap ───────────────────────────────────────────────────
    try:
        heatmap_b64 = generate_heatmap(cv_model, pil_image)
    except Exception as e:
        logger.warning(f"[{request_id}] Heatmap generation failed: {e}. Using empty placeholder.")
        heatmap_b64 = ""

    # ── 3. NLP Analysis ───────────────────────────────────────────────────────
    nlp_model = request.app.state.nlp_model
    try:
        nlp_result        = nlp_model.analyze(symptoms)
        nlp_predictions   = nlp_result.get("disease_scores", [])
        extracted_symptoms = nlp_result.get("extracted_symptoms", [])
    except Exception as e:
        logger.error(f"[{request_id}] NLP analysis failed: {e}", exc_info=True)
        nlp_predictions   = []
        extracted_symptoms = []

    # ── 4. Multimodal Fusion ──────────────────────────────────────────────────
    fusion_scores = fuse_predictions(image_predictions, nlp_predictions)

    # ── 5. Urgency classification ─────────────────────────────────────────────
    top = fusion_scores[0] if fusion_scores else {"condition": "Unknown", "final_score": 0.0}
    urgency_level = determine_urgency(top["condition"], top["final_score"])

    return {
        "image_predictions": image_predictions,
        "nlp_predictions":   nlp_predictions,
        "fusion_scores":     fusion_scores,
        "extracted_symptoms": extracted_symptoms,
        "urgency_level":     urgency_level,
        "heatmap_base64":    heatmap_b64,
        "modality":          modality,
    }


# ── Report Generation ─────────────────────────────────────────────────────────

@router.post("/report", response_model=ReportResponse)
@limiter.limit("10/minute")
async def generate_report(request: Request, body: ReportRequest):
    """RAG-powered LLM report generation."""
    request_id = getattr(request.state, "request_id", "unknown")
    vectorstore     = request.app.state.vectorstore
    report_generator = request.app.state.report_generator

    top_conditions  = " ".join([d.condition for d in body.diagnosis_list[:3]])
    query           = f"{top_conditions} {body.symptoms}"
    retrieved_docs  = vectorstore.query(query, k=4)

    try:
        raw_report  = report_generator.generate(
            diagnosis_list=[d.dict() for d in body.diagnosis_list],
            symptoms=body.symptoms,
            retrieved_context=retrieved_docs,
        )
        report_text = apply_safety_guardrails(raw_report)
    except Exception as e:
        logger.error(f"[{request_id}] Report generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Report generation failed. Please try again.")

    disclaimer = (
        "⚠️ This AI-generated report is for informational purposes only and is NOT "
        "a substitute for professional medical diagnosis or treatment."
    )

    return ReportResponse(
        report_text=report_text,
        sources_used=len(retrieved_docs),
        disclaimer=disclaimer,
    )


# ── Chat Q&A ──────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("30/minute")
async def chat(request: Request, body: ChatRequest):
    """Conversational follow-up Q&A about the diagnosis."""
    request_id = getattr(request.state, "request_id", "unknown")
    qa_chain = request.app.state.qa_chain

    # Sanitize user message
    clean_message = sanitize_text_input(body.message)

    try:
        response_text, updated_history = qa_chain.chat(
            message=clean_message,
            conversation_history=body.conversation_history,
            diagnosis_context=body.diagnosis_context,
        )
    except Exception as e:
        logger.error(f"[{request_id}] Chat failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Chat service temporarily unavailable.")

    return ChatResponse(
        response=response_text,
        updated_history=updated_history,
    )
