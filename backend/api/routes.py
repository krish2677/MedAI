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
from utils.safety import (
    apply_safety_guardrails,
    validate_symptoms_input,
    validate_modality,
)
from PIL import Image

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """Returns model loading status and API version."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        models_loaded={
            "cv_model": hasattr(request.app.state, "cv_model") and request.app.state.cv_model.is_loaded,
            "nlp_model": hasattr(request.app.state, "nlp_model") and request.app.state.nlp_model.is_loaded,
            "vectorstore": hasattr(request.app.state, "vectorstore"),
        },
    )


@router.post("/analyze")
async def analyze(
    request: Request,
    image: UploadFile = File(...),
    symptoms: str = Form(...),
    modality: str = Form("chest_xray"),
):
    """
    Full multimodal analysis pipeline:
    1. CV inference → 2. Grad-CAM → 3. NLP → 4. Fusion → 5. Urgency
    """
    # Validation
    valid_mod, mod_err = validate_modality(modality)
    if not valid_mod:
        raise HTTPException(status_code=400, detail=mod_err)

    valid_sym, sym_err = validate_symptoms_input(symptoms)
    if not valid_sym:
        raise HTTPException(status_code=400, detail=sym_err)

    image_bytes = await image.read()
    if not validate_image_size(image_bytes):
        raise HTTPException(status_code=413, detail="Image file exceeds 10MB limit.")

    try:
        pil_image = load_image_from_bytes(image_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 1. CV Inference
    if modality == "skin" and hasattr(request.app.state, "skin_model"):
        cv_model = request.app.state.skin_model
    elif modality == "retina" and hasattr(request.app.state, "retina_model"):
        cv_model = request.app.state.retina_model
    else:
        cv_model = request.app.state.cv_model
    try:
        image_predictions = cv_model.predict(pil_image)
    except Exception as e:
        logger.error(f"CV inference failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {e}")

    # 2. Grad-CAM heatmap
    try:
        heatmap_b64 = generate_heatmap(cv_model, pil_image)
    except Exception as e:
        logger.warning(f"Heatmap generation failed: {e}. Using placeholder.")
        heatmap_b64 = ""

    # 3. NLP Analysis
    nlp_model = request.app.state.nlp_model
    try:
        nlp_result = nlp_model.analyze(symptoms)
        nlp_predictions = nlp_result.get("disease_scores", [])
        extracted_symptoms = nlp_result.get("extracted_symptoms", [])
    except Exception as e:
        logger.error(f"NLP analysis failed: {e}")
        nlp_predictions = []
        extracted_symptoms = []

    # 4. Multimodal Fusion
    fusion_scores = fuse_predictions(image_predictions, nlp_predictions)

    # 5. Urgency classification
    top = fusion_scores[0] if fusion_scores else {"condition": "Unknown", "final_score": 0.0}
    urgency_level = determine_urgency(top["condition"], top["final_score"])

    return {
        "image_predictions": image_predictions,
        "nlp_predictions": nlp_predictions,
        "fusion_scores": fusion_scores,
        "extracted_symptoms": extracted_symptoms,
        "urgency_level": urgency_level,
        "heatmap_base64": heatmap_b64,
        "modality": modality,
    }


@router.post("/report", response_model=ReportResponse)
async def generate_report(request: Request, body: ReportRequest):
    """RAG-powered LLM report generation."""
    vectorstore = request.app.state.vectorstore
    report_generator = request.app.state.report_generator

    # Build query for RAG retrieval
    top_conditions = " ".join([d.condition for d in body.diagnosis_list[:3]])
    query = f"{top_conditions} {body.symptoms}"

    retrieved_docs = vectorstore.query(query, k=4)

    try:
        raw_report = report_generator.generate(
            diagnosis_list=[d.dict() for d in body.diagnosis_list],
            symptoms=body.symptoms,
            retrieved_context=retrieved_docs,
        )
        report_text = apply_safety_guardrails(raw_report)
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")

    disclaimer = (
        "⚠️ This AI-generated report is for informational purposes only and is NOT "
        "a substitute for professional medical diagnosis or treatment."
    )

    return ReportResponse(
        report_text=report_text,
        sources_used=len(retrieved_docs),
        disclaimer=disclaimer,
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest):
    """Conversational follow-up Q&A about the diagnosis."""
    qa_chain = request.app.state.qa_chain

    try:
        response_text, updated_history = qa_chain.chat(
            message=body.message,
            conversation_history=body.conversation_history,
            diagnosis_context=body.diagnosis_context,
        )
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")

    return ChatResponse(
        response=response_text,
        updated_history=updated_history,
    )
