import os
from functools import lru_cache
from pathlib import Path

BASE_MODEL = "ai4bharat/indic-bert"
MODEL_ID = os.getenv("TRIAGE_MODEL", str(Path("models/triage-synthetic")))
LABELS = ["LEVEL_1_EMERGENCY", "LEVEL_2_URGENT", "LEVEL_3_PRIMARY_CARE", "LEVEL_4_ROUTINE"]

@lru_cache(maxsize=1)
def _load_classifier():
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    path = MODEL_ID if Path(MODEL_ID).exists() else BASE_MODEL
    tokenizer = AutoTokenizer.from_pretrained(path, token=os.getenv("HF_TOKEN"))
    model = AutoModelForSequenceClassification.from_pretrained(path, token=os.getenv("HF_TOKEN"))
    return tokenizer, model, path

EMERGENCY_KEYWORDS = ["chest pain", "difficulty breathing", "unconscious", "severe bleeding", "seizure", "stroke"]
URGENT_KEYWORDS = ["high fever", "persistent vomiting", "severe pain", "dizziness"]

def analyze_triage(text, language, vitals=None, history=None):
    vitals, history = vitals or {}, history or []
    if not text.strip():
        return {"triage_level": "LEVEL_4_ROUTINE", "confidence": 0.0, "reason_codes": [], "red_flags": [], "recommended_action": "Human review required.", "model": MODEL_ID, "model_status": "empty_input"}

    try:
        import torch
        tokenizer, model, loaded_path = _load_classifier()
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        with torch.no_grad():
            logits = model(**inputs).logits
            probs = torch.softmax(logits, dim=-1)[0]
        idx = int(torch.argmax(probs).item())
        confidence = float(probs[idx].item())
        return {"triage_level": LABELS[idx], "confidence": round(confidence, 4), "reason_codes": ["MODEL_PREDICTION"], "red_flags": [], "recommended_action": "Requires healthcare professional review.", "model": loaded_path, "model_status": "loaded"}
    except Exception as exc:
        low = text.lower()
        red = [x for x in EMERGENCY_KEYWORDS if x in low]
        if red:
            level = "LEVEL_1_EMERGENCY"
        elif any(x in low for x in URGENT_KEYWORDS):
            level = "LEVEL_2_URGENT"
        else:
            level = "LEVEL_3_PRIMARY_CARE"
        return {"triage_level": level, "confidence": 0.0, "reason_codes": ["SAFE_FALLBACK"], "red_flags": red, "recommended_action": "Model unavailable; requires human review.", "model": MODEL_ID, "model_status": f"fallback: {type(exc).__name__}"}
