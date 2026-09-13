EMERGENCY_TERMS = {"unconscious":"unconsciousness","severe bleeding":"severe_bleeding","difficulty breathing":"breathing_difficulty","shortness of breath":"breathing_difficulty","chest pain":"chest_pain","seizure":"seizure","stroke":"stroke_sign","மூச்சுத்திணறல்":"breathing_difficulty","மூச்சு விட சிரமம்":"breathing_difficulty","மார்பு வலி":"chest_pain","மயக்கம்":"unconsciousness","विकलता":"breathing_difficulty","सांस लेने में कठिनाई":"breathing_difficulty","सीने में दर्द":"chest_pain","बेहोश":"unconsciousness","श्वास घेण्यास त्रास":"breathing_difficulty","छातीत दुखणे":"chest_pain","बेशुद्ध":"unconsciousness","శ్వాస తీసుకోవడంలో ఇబ్బంది":"breathing_difficulty","ఛాతి నొప్పి":"chest_pain","స్పృహ కోల్పోవడం":"unconsciousness","ಉಸಿರಾಟದ ತೊಂದರೆ":"breathing_difficulty","ಎದೆ ನೋವು":"chest_pain","ಪ್ರಜ್ಞೆ ತಪ್ಪುವುದು":"unconsciousness","শ্বাস নিতে কষ্ট":"breathing_difficulty","বুকে ব্যথা":"chest_pain","অজ্ঞান":"unconsciousness","ശ്വാസംമുട്ടൽ":"breathing_difficulty","നെഞ്ചുവേദന":"chest_pain","ബോധരഹിത":"unconsciousness"}


def apply_safety(ai_result: dict, text: str, vitals: dict):
    t = (text or "").casefold()
    flags = set(ai_result.get("red_flags", []))
    flags.update(code for term, code in EMERGENCY_TERMS.items() if term.casefold() in t)
    if flags:
        ai_result["triage_level"] = "LEVEL_1_EMERGENCY"
        ai_result["risk_score"] = 100
        ai_result["risk_level"] = "CRITICAL"
        ai_result["risk_label"] = "Immediate emergency attention"
        ai_result["confidence_percent"] = 100.0
        ai_result["recommended_action"] = "Immediate emergency evaluation. Human/ASHA verification is required."
        ai_result["human_review_required"] = True
        ai_result["model_status"] = "safety_override"
    elif not ai_result.get("confidence") or ai_result.get("confidence", 0) < 0.60:
        ai_result["recommended_action"] = "Requires human review. Do not use this system as a diagnosis."
        ai_result["human_review_required"] = True
    ai_result["red_flags"] = sorted(flags)
    ai_result["safety_checked"] = True
    ai_result["disclaimer"] = "AI-assisted decision support. Not a medical diagnosis."
    return ai_result
