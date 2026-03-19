from pydantic import BaseModel, Field
from typing import Optional, List


class DiagnosisItem(BaseModel):
    condition: str
    final_score: float


class ImagePrediction(BaseModel):
    condition: str
    confidence: float
    source: str


class AnalysisResponse(BaseModel):
    image_predictions: List[ImagePrediction]
    nlp_predictions: List[dict]
    fusion_scores: List[DiagnosisItem]
    extracted_symptoms: List[str]
    urgency_level: str  # "LOW" | "MODERATE" | "HIGH"
    heatmap_base64: str
    modality: str


class ReportRequest(BaseModel):
    diagnosis_list: List[DiagnosisItem]
    symptoms: str
    patient_context: Optional[str] = None


class ReportResponse(BaseModel):
    report_text: str
    sources_used: int
    disclaimer: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: List[dict] = Field(default_factory=list)
    diagnosis_context: str


class ChatResponse(BaseModel):
    response: str
    updated_history: List[dict]


class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: dict
