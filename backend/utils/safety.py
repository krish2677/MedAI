"""
Safety guardrail functions for the medical AI assistant.
Ensures responses never prescribe medications and always include disclaimers.
"""

import re
import logging

logger = logging.getLogger(__name__)

DISCLAIMER = (
    "\n\n⚠️ DISCLAIMER: This AI-generated report is for informational purposes only "
    "and is NOT a substitute for professional medical diagnosis, advice, or treatment. "
    "Always consult a qualified healthcare provider."
)

MEDICATION_PATTERNS = [
    r"\b(prescribe|prescription|take \d+mg|dose of \d+|administer \d+)\b",
    r"\b(amoxicillin|ibuprofen|aspirin|metformin|lisinopril|atorvastatin)\b",
    r"\b\d+\s*(mg|mcg|g|ml|units?)\s*(daily|twice|three times|per day|bid|tid|qd)\b",
]

DEFINITIVE_DIAGNOSIS_PATTERNS = [
    r"\byou have\b(?! been)",
    r"\byou are diagnosed with\b",
    r"\bthe diagnosis is\b",
    r"\bconfirmed diagnosis\b",
]

PROBABILISTIC_REPLACEMENTS = {
    "you have ": "findings suggest you may have ",
    "you are diagnosed with ": "the AI findings are consistent with ",
    "the diagnosis is ": "the probable diagnosis based on AI analysis is ",
    "confirmed diagnosis": "probable finding",
}


def check_for_medication_advice(text: str) -> bool:
    """Returns True if text contains specific medication prescriptions."""
    text_lower = text.lower()
    for pattern in MEDICATION_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def make_language_probabilistic(text: str) -> str:
    """Replace definitive diagnostic language with probabilistic alternatives."""
    for phrase, replacement in PROBABILISTIC_REPLACEMENTS.items():
        text = re.sub(re.escape(phrase), replacement, text, flags=re.IGNORECASE)
    return text


def apply_safety_guardrails(text: str) -> str:
    """
    Apply all safety guardrails to a generated text:
    1. Make language probabilistic
    2. Check for and flag medication advice
    3. Ensure disclaimer is present
    """
    text = make_language_probabilistic(text)

    if check_for_medication_advice(text):
        logger.warning("Response contained medication advice — redacting.")
        text = re.sub(
            r"\b\d+\s*(mg|mcg|g|ml|units?)\b",
            "[DOSAGE REDACTED]",
            text,
            flags=re.IGNORECASE,
        )

    if DISCLAIMER.strip() not in text:
        text += DISCLAIMER

    return text


def validate_symptoms_input(symptoms: str) -> tuple[bool, str]:
    """Basic validation for symptom input."""
    if not symptoms or not symptoms.strip():
        return False, "Symptoms description cannot be empty."
    if len(symptoms.strip()) < 5:
        return False, "Please provide a more detailed symptom description."
    if len(symptoms) > 5000:
        return False, "Symptom description is too long (max 5000 characters)."
    return True, ""


def validate_modality(modality: str) -> tuple[bool, str]:
    """Validate that the imaging modality is supported."""
    supported = {"chest_xray", "skin", "retina"}
    if modality not in supported:
        return False, f"Unsupported modality '{modality}'. Choose from: {', '.join(supported)}."
    return True, ""
