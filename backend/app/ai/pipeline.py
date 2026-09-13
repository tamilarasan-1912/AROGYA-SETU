from app.ai.symptoms.extractor import extract_symptoms
from app.ai.triage.model import analyze_triage
from app.ai.triage.safety_rules import apply_safety
from app.referral.engine import recommend_referral
from app.services.storage import store_encounter


def run_clinical_decision_pipeline(text: str, language: str, patient_id: str | None = None, vitals: dict | None = None, history: list | None = None, location: str = "", specialty: str | None = None) -> dict:
    vitals = vitals or {}
    history = history or []

    symptoms = extract_symptoms(text)
    triage = analyze_triage(text, language, vitals, history)
    triage = apply_safety(triage, text, vitals)
    referral = recommend_referral(triage["triage_level"], symptoms["symptoms"], location, specialty)

    encounter = None
    if patient_id:
        encounter = store_encounter({
            "patient_id": patient_id,
            "original_language": language,
            "original_transcript": text,
            "normalized_data": {
                "symptoms": symptoms["symptoms"],
                "vitals": vitals,
                "triage": triage,
                "referral": referral,
            },
            "record_type": "ai_triage_encounter",
        })

    return {
        "pipeline": ["symptom_extraction", "triage", "safety", "referral", "recording"],
        "language": language,
        "transcript": text,
        "symptoms": symptoms,
        "triage": triage,
        "referral": referral,
        "encounter": encounter,
        "decision_support_only": True,
    }
