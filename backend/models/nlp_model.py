import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# Comprehensive symptom-to-disease mapping (50+ entries)
SYMPTOM_TO_DISEASE_MAP = {
    "chest pain": ["Myocardial Infarction", "Pneumothorax", "Pericarditis", "Angina"],
    "shortness of breath": ["Pneumonia", "Edema", "Emphysema", "Atelectasis", "Heart Failure"],
    "dyspnea": ["Pneumonia", "Edema", "Emphysema", "Atelectasis", "Pulmonary Embolism"],
    "cough": ["Pneumonia", "Tuberculosis", "Lung Cancer", "Bronchitis", "COPD"],
    "productive cough": ["Pneumonia", "Bronchitis", "Tuberculosis", "Cystic Fibrosis"],
    "fever": ["Pneumonia", "Influenza", "COVID-19", "Sepsis", "Tuberculosis"],
    "fatigue": ["Anemia", "Hypothyroidism", "Diabetes", "Heart Failure", "Lymphoma"],
    "weight loss": ["Tuberculosis", "Lung Cancer", "Lymphoma", "Diabetes", "Hyperthyroidism"],
    "night sweats": ["Tuberculosis", "Lymphoma", "Endocarditis", "HIV"],
    "hemoptysis": ["Tuberculosis", "Lung Cancer", "Pulmonary Embolism", "Bronchiectasis"],
    "wheezing": ["Asthma", "COPD", "Emphysema", "Bronchitis"],
    "rales": ["Pneumonia", "Edema", "Atelectasis", "Fibrosis"],
    "pleural effusion": ["Pneumonia", "Heart Failure", "Malignancy", "Tuberculosis"],
    "palpitations": ["Arrhythmia", "Heart Failure", "Hyperthyroidism", "Anemia"],
    "edema": ["Heart Failure", "Renal Failure", "Cirrhosis", "Hypoalbuminemia"],
    "ankle swelling": ["Heart Failure", "Deep Vein Thrombosis", "Venous Insufficiency"],
    "cyanosis": ["Pneumothorax", "Pulmonary Embolism", "Congenital Heart Disease", "ARDS"],
    "hypoxia": ["Pneumonia", "Pulmonary Embolism", "ARDS", "Heart Failure"],
    "tachycardia": ["Sepsis", "Pulmonary Embolism", "Anemia", "Hyperthyroidism"],
    "bradycardia": ["Hypothyroidism", "Heart Block", "Increased ICP"],
    "hypertension": ["Renal Disease", "Primary Hypertension", "Cushing's Syndrome"],
    "hypotension": ["Septic Shock", "Cardiogenic Shock", "Hemorrhage", "Adrenal Insufficiency"],
    "syncope": ["Cardiac Arrhythmia", "Vasovagal Syncope", "Orthostatic Hypotension"],
    "headache": ["Hypertension", "Migraine", "Meningitis", "Brain Tumor"],
    "confusion": ["Sepsis", "Encephalopathy", "Stroke", "Dementia"],
    "dizziness": ["Vertigo", "Anemia", "Orthostatic Hypotension", "Cardiac Arrhythmia"],
    "nausea": ["Appendicitis", "Gastroenteritis", "Myocardial Infarction", "Hepatitis"],
    "vomiting": ["Gastroenteritis", "Bowel Obstruction", "Pancreatitis", "Increased ICP"],
    "abdominal pain": ["Appendicitis", "Pancreatitis", "Bowel Obstruction", "Cholecystitis"],
    "jaundice": ["Hepatitis", "Cholecystitis", "Cirrhosis", "Pancreatic Cancer"],
    "skin rash": ["Cellulitis", "Melanoma", "Eczema", "Drug Reaction", "Psoriasis"],
    "skin lesion": ["Melanoma", "Basal Cell Carcinoma", "Squamous Cell Carcinoma", "Eczema"],
    "mole": ["Melanoma", "Melanocytic Nevus", "Seborrheic Keratosis"],
    "itching": ["Eczema", "Contact Dermatitis", "Psoriasis", "Cholestasis"],
    "joint pain": ["Rheumatoid Arthritis", "Osteoarthritis", "Gout", "Lupus"],
    "muscle weakness": ["Myopathy", "Motor Neuron Disease", "Guillain-Barre", "Stroke"],
    "back pain": ["Herniated Disc", "Spinal Stenosis", "Kidney Stone", "Muscle Strain"],
    "neck stiffness": ["Meningitis", "Cervical Spondylosis", "Subarachnoid Hemorrhage"],
    "vision changes": ["Diabetic Retinopathy", "Glaucoma", "Macular Degeneration", "Stroke"],
    "vision": ["Diabetic Retinopathy", "Glaucoma", "Cataract"],
    "blurred vision": ["Diabetic Retinopathy", "Cataract", "Glaucoma", "Hypertension"],
    "fluctuating vision": ["Diabetic Retinopathy", "Diabetes Mellitus"],
    "dark spots": ["Diabetic Retinopathy", "Retinal Detachment", "Macular Degeneration"],
    "floaters": ["Diabetic Retinopathy", "Retinal Detachment"],
    "diabetes": ["Diabetic Retinopathy", "Diabetes Mellitus"],
    "eye pain": ["Glaucoma", "Uveitis"],
    "halos": ["Glaucoma", "Cataract"],
    "loss of vision": ["Glaucoma", "Diabetic Retinopathy", "Retinal Detachment"],
    "retinal hemorrhage": ["Diabetic Retinopathy", "Hypertensive Retinopathy", "Vein Occlusion"],
    "papilledema": ["Increased ICP", "Hypertensive Crisis", "Brain Tumor"],
    "polyuria": ["Diabetes Mellitus", "Diabetes Insipidus", "Chronic Kidney Disease"],
    "polydipsia": ["Diabetes Mellitus", "Diabetes Insipidus", "Hypercalcemia"],
    "dysuria": ["Urinary Tract Infection", "Sexually Transmitted Infection", "Prostatitis"],
    "hematuria": ["Urinary Tract Infection", "Kidney Stones", "Bladder Cancer", "Glomerulonephritis"],
    "lymphadenopathy": ["Lymphoma", "Infection", "Leukemia", "Metastatic Cancer"],
    "pallor": ["Anemia", "Leukemia", "Sepsis", "Hypothyroidism"],
    "clubbing": ["COPD", "Cystic Fibrosis", "Lung Cancer", "Congenital Heart Disease"],
    "crepitus": ["Pneumonia", "Pleuritis", "Subcutaneous Emphysema"],
    "crackles": ["Pneumonia", "Pulmonary Edema", "Pulmonary Fibrosis"],
}

# Medical NER keyword patterns for symptom extraction
SYMPTOM_KEYWORDS = list(SYMPTOM_TO_DISEASE_MAP.keys()) + [
    "pain", "ache", "swelling", "inflammation", "bleeding", "discharge",
    "numbness", "tingling", "redness", "bruising", "lump", "mass",
    "difficulty breathing", "chest tightness", "irregular heartbeat",
]


class NLPModel:
    """
    BioBERT-based NLP model for symptom extraction and disease mapping.
    Falls back to rule-based extraction when the model is unavailable.
    """

    def __init__(self):
        self._pipeline = None
        self._load_ner_pipeline()

    def _load_ner_pipeline(self):
        """Attempt to load the Medical NER pipeline from HuggingFace."""
        try:
            from transformers import pipeline
            logger.info("Loading Medical NER pipeline...")
            self._pipeline = pipeline(
                "ner",
                model="blaze999/Medical-NER",
                tokenizer="blaze999/Medical-NER",
                aggregation_strategy="simple",
            )
            logger.info("Medical NER pipeline loaded successfully.")
        except Exception as e:
            logger.warning(
                f"Could not load Medical NER model ({e}). "
                "Falling back to rule-based keyword extraction."
            )
            self._pipeline = None

    def extract_symptoms(self, text: str) -> list:
        """Extract medical entities/symptoms from free text."""
        extracted = []

        # Try NER pipeline first
        if self._pipeline is not None:
            try:
                entities = self._pipeline(text)
                extracted = [
                    e["word"].lower()
                    for e in entities
                    if e["entity_group"] in ["SYMPTOM", "SIGN", "DISEASE", "PROBLEM"]
                ]
            except Exception as e:
                logger.warning(f"NER pipeline failed: {e}")

        # Always supplement with rule-based extraction
        text_lower = text.lower()
        for keyword in SYMPTOM_KEYWORDS:
            if keyword in text_lower and keyword not in extracted:
                extracted.append(keyword)

        return list(set(extracted))

    def symptoms_to_disease_scores(self, symptoms: list) -> list:
        """Map extracted symptoms to disease probability scores."""
        disease_scores = {}
        for symptom in symptoms:
            for key, diseases in SYMPTOM_TO_DISEASE_MAP.items():
                if key in symptom or symptom in key:
                    for disease in diseases:
                        disease_scores[disease] = disease_scores.get(disease, 0) + 1

        total = sum(disease_scores.values()) or 1
        results = [
            {
                "condition": d,
                "confidence": round(s / total, 3),
                "source": "nlp_model"
            }
            for d, s in disease_scores.items()
        ]
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results[:5]

    def analyze(self, text: str) -> dict:
        symptoms = self.extract_symptoms(text)
        disease_scores = self.symptoms_to_disease_scores(symptoms)
        return {
            "extracted_symptoms": symptoms,
            "disease_scores": disease_scores
        }

    @property
    def is_loaded(self) -> bool:
        return True  # Always "loaded" because we have rule-based fallback
