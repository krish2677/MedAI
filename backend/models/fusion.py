HIGH_URGENCY_CONDITIONS = {
    "Pneumothorax", "Edema", "Pulmonary Edema", "Myocardial Infarction",
    "Melanoma", "Sepsis", "Septic Shock", "Cardiogenic Shock",
    "Pulmonary Embolism", "ARDS", "Hemorrhage", "Meningitis",
    "Subarachnoid Hemorrhage", "Brain Tumor", "Increased ICP",
    "Acute Respiratory Failure", "Cardiac Tamponade",
}

MODERATE_CONDITIONS = {
    "Pneumonia", "Consolidation", "Emphysema", "Atelectasis",
    "Pleural Thickening", "Cardiomegaly", "Diabetes Mellitus",
    "Tuberculosis", "Heart Failure", "Effusion", "Lymphoma",
    "Lung Cancer", "Pancreatic Cancer", "Hepatitis", "Cirrhosis",
    "Bowel Obstruction", "Deep Vein Thrombosis", "Basal Cell Carcinoma",
    "Squamous Cell Carcinoma", "Leukemia", "Anemia", "Renal Failure",
}


def fuse_predictions(
    image_predictions: list,
    nlp_predictions: list,
    image_weight: float = 0.65,
    nlp_weight: float = 0.35,
) -> list:
    """
    Weighted ensemble fusion of image model and NLP model outputs.
    Returns top 5 fused conditions sorted by final_score.
    """
    combined = {}

    for pred in image_predictions:
        cond = pred["condition"]
        combined[cond] = combined.get(cond, 0.0) + pred["confidence"] * image_weight

    for pred in nlp_predictions:
        cond = pred["condition"]
        combined[cond] = combined.get(cond, 0.0) + pred["confidence"] * nlp_weight

    fused = [
        {"condition": cond, "final_score": round(score, 4)}
        for cond, score in combined.items()
    ]
    fused.sort(key=lambda x: x["final_score"], reverse=True)
    return fused[:5]


def determine_urgency(top_condition: str, confidence: float) -> str:
    """
    Classify urgency as LOW / MODERATE / HIGH based on condition and confidence.
    """
    if top_condition in HIGH_URGENCY_CONDITIONS and confidence > 0.5:
        return "HIGH"
    elif top_condition in HIGH_URGENCY_CONDITIONS:
        return "MODERATE"
    elif top_condition in MODERATE_CONDITIONS or confidence > 0.70:
        return "MODERATE"
    return "LOW"
