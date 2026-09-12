# Deterministic safety layer. These phrases are conservative demo rules, not a clinical protocol.
EMERGENCY_TERMS = {
    "unconscious", "severe bleeding", "difficulty breathing", "chest pain", "seizure", "stroke",
    "सीने में दर्द", "सांस लेने में कठिनाई", "बेहोश", "बहुत ज्यादा खून", "दौरा", "स्ट्रोक",
    "छातीत दुख", "श्वास घेण्यास त्रास", "बेशुद्ध", "रक्तस्राव",
    "மார்பு வலி", "மூச்சுத்திணறல்", "மயக்கம்", "அதிக இரத்தப்போக்கு",
    "ఛాతీ నొప్పి", "శ్వాస తీసుకోవడంలో ఇబ్బంది", "స్పృహలో లేరు", "తీవ్రమైన రక్తస్రావం",
    "ಎದೆ ನೋವು", "ಉಸಿರಾಟದ ತೊಂದರೆ", "ಪ್ರಜ್ಞಾಹೀನ", "ತೀವ್ರ ರಕ್ತಸ್ರಾವ",
    "বুকে ব্যথা", "শ্বাসকষ্ট", "অচেতন", "তীব্র রক্তপাত",
    "നെഞ്ചുവേദന", "ശ്വാസതടസ്സം", "ബോധരഹിത", "കടുത്ത രക്തസ്രാവം",
    "છાતીમાં દુખાવો", "શ્વાસ લેવામાં તકલીફ", "બેભાન", "ભારે રક્તસ્રાવ",
}

def apply_safety(ai_result: dict, text: str, vitals: dict):
    t = text.lower()
    flags = set(ai_result.get("red_flags", []))
    flags.update(term for term in EMERGENCY_TERMS if term.lower() in t)
    if flags:
        ai_result["triage_level"] = "LEVEL_1_EMERGENCY"
        ai_result["recommended_action"] = "Immediate emergency evaluation. Human/ASHA verification is required."
    elif ai_result.get("confidence", 0) < 0.60:
        ai_result["recommended_action"] = "Requires human review. Do not use this system as a diagnosis."
    ai_result["red_flags"] = sorted(flags)
    ai_result["safety_checked"] = True
    ai_result["disclaimer"] = "AI-assisted decision support. Not a medical diagnosis."
    return ai_result
