EMERGENCY_TERMS = {"unconscious","severe bleeding","difficulty breathing","chest pain","seizure","stroke"}

def apply_safety(ai_result: dict, text: str, vitals: dict):
    t = text.lower()
    flags = set(ai_result.get("red_flags", []))
    flags.update(term for term in EMERGENCY_TERMS if term in t)
    if flags:
        ai_result["triage_level"] = "LEVEL_1_EMERGENCY"
        ai_result["recommended_action"] = "Immediate emergency evaluation. Human/ASHA verification is required."
    elif not ai_result.get("confidence") or ai_result.get("confidence", 0) < 0.60:
        ai_result["recommended_action"] = "Requires human review. Do not use this system as a diagnosis."
    ai_result["red_flags"] = sorted(flags)
    ai_result["safety_checked"] = True
    ai_result["disclaimer"] = "AI-assisted decision support. Not a medical diagnosis."
    return ai_result
