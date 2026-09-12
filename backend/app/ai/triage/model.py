import os
from functools import lru_cache

BASE_MODEL_ID = "ai4bharat/indic-bert"
MODEL_PATH = os.getenv("TRIAGE_MODEL_PATH", "models/triage-synthetic")
LABELS = [
    "LEVEL_1_EMERGENCY",
    "LEVEL_2_URGENT",
    "LEVEL_3_PRIMARY_CARE",
    "LEVEL_4_ROUTINE",
]

@lru_cache(maxsize=1)
def _load_classifier():
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    source = MODEL_PATH if os.path.isdir(MODEL_PATH) else BASE_MODEL_ID
    tokenizer = AutoTokenizer.from_pretrained(source, token=os.getenv("HF_TOKEN"))
    model = AutoModelForSequenceClassification.from_pretrained(
        source,
        num_labels=len(LABELS),
        ignore_mismatched_sizes=True,
        token=os.getenv("HF_TOKEN"),
    )
    model.eval()
    return tokenizer, model, source


def analyze_triage(text, language, vitals=None, history=None):
    vitals = vitals or {}
    history = history or []
    text = (text or "").strip()

    red_flag_terms = {
        "chest pain": "chest_pain",
        "difficulty breathing": "breathing_difficulty",
        "shortness of breath": "breathing_difficulty",
        "unconscious": "unconsciousness",
        "seizure": "seizure",
        "severe bleeding": "severe_bleeding",
        "stroke": "stroke_sign",
    }
    low = text.lower()
    red_flags = [code for term, code in red_flag_terms.items() if term in low]

    # Safety-first: explicit red flags override statistical model output.
    if red_flags:
        return {
            "triage_level": "LEVEL_1_EMERGENCY",
            "confidence": 1.0,
            "reason_codes": red_flags,
            "red_flags": red_flags,
            "recommended_action": "Seek emergency medical care immediately. Human clinical review is required.",
            "model": BASE_MODEL_ID,
            "model_status": "safety_override",
            "decision_support_only": True,
        }

    try:
        tokenizer, model, source = _load_classifier()
        import torch
        with torch.inference_mode():
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
            logits = model(**inputs).logits
            probabilities = torch.softmax(logits, dim=-1)[0]
            confidence, index = torch.max(probabilities, dim=-1)
            confidence = float(confidence)
            predicted = LABELS[int(index)]

        if confidence < 0.60 or source == BASE_MODEL_ID:
            predicted = "LEVEL_3_PRIMARY_CARE" if text else "LEVEL_4_ROUTINE"
            recommended = "Requires healthcare professional review because the classifier is unavailable, untrained, or below the confidence threshold."
        else:
            recommended = "Use this result only as decision support and confirm with a healthcare professional."

        return {
            "triage_level": predicted,
            "confidence": round(confidence, 4),
            "reason_codes": [],
            "red_flags": [],
            "recommended_action": recommended,
            "model": source,
            "model_status": "loaded",
            "decision_support_only": True,
        }
    except Exception as exc:
        return {
            "triage_level": "LEVEL_3_PRIMARY_CARE" if text else "LEVEL_4_ROUTINE",
            "confidence": 0.0,
            "reason_codes": ["MODEL_UNAVAILABLE"],
            "red_flags": [],
            "recommended_action": "AI model unavailable. Requires healthcare professional review.",
            "model": BASE_MODEL_ID,
            "model_status": f"unavailable: {type(exc).__name__}",
            "decision_support_only": True,
        }
