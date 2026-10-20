from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class DiagnosisItem(BaseModel):
    condition: str = Field(..., max_length=256)
    final_score: float = Field(..., ge=0.0, le=1.0)


class ImagePrediction(BaseModel):
    condition: str = Field(..., max_length=256)
    confidence: float = Field(..., ge=0.0, le=1.0)
    source: str = Field(..., max_length=64)


class AnalysisResponse(BaseModel):
    image_predictions: List[ImagePrediction]
    nlp_predictions: List[dict]
    fusion_scores: List[DiagnosisItem]
    extracted_symptoms: List[str]
    urgency_level: str  # "LOW" | "MODERATE" | "HIGH"
    heatmap_base64: str
    modality: str


class ReportRequest(BaseModel):
    diagnosis_list: List[DiagnosisItem] = Field(..., max_length=10)
    symptoms: str = Field(..., min_length=5, max_length=5000)
    patient_context: Optional[str] = Field(None, max_length=2000)

    @field_validator("symptoms")
    @classmethod
    def strip_symptoms(cls, v: str) -> str:
        return v.strip()


class ReportResponse(BaseModel):
    report_text: str
    sources_used: int
    disclaimer: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_history: List[dict] = Field(default_factory=list, max_length=20)
    diagnosis_context: str = Field(..., max_length=4000)

    @field_validator("message")
    @classmethod
    def strip_message(cls, v: str) -> str:
        return v.strip()


class ChatResponse(BaseModel):
    response: str
    updated_history: List[dict]


class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: dict
