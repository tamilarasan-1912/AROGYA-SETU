import re

# Prototype symptom ontology. Keep outputs structured and conservative.
SYMPTOMS = {
    "fever": ["fever", "high temperature", "காய்ச்சல்", "बुखार", "ताप", "జ్వరం", "ಜ್ವರ", "জ্বর", "പനി"],
    "cough": ["cough", "কাশি", "இருமல்", "खांसी", "దగ్గు", "ಕೆಮ್ಮು", "ചുമ"],
    "chest_pain": ["chest pain", "மார்பு வலி", "सीने में दर्द", "छातीत दुखणे", "ఛాతి నొప్పి", "ಎದೆ ನೋವು", "বুকে ব্যথা", "നെഞ്ചുവേദന"],
    "breathing_difficulty": ["difficulty breathing", "shortness of breath", "மூச்சுத்திணறல்", "सांस लेने में कठिनाई", "श्वास घेण्यास त्रास", "శ్వాస తీసుకోవడంలో ఇబ్బంది", "ಉಸಿರಾಟದ ತೊಂದರೆ", "শ্বাস নিতে কষ্ট", "ശ്വാസംമുട്ടൽ"],
    "headache": ["headache", "தலைவலி", "सिरदर्द", "डोकेदुखी", "తలనొప్పి", "ತಲೆನೋವು", "মাথাব্যথা", "തലവേദന"],
    "vomiting": ["vomiting", "vomit", "வாந்தி", "उल्टी", "వాంతులు", "ವಾಂತಿ", "বমি", "ഛർദ്ദി"],
    "diarrhea": ["diarrhea", "loose motion", "வயிற்றுப்போக்கு", "दस्त", "అతిసారం", "ಅತಿಸಾರ", "ডায়রিয়া", "വയറിളക്കം"],
    "abdominal_pain": ["abdominal pain", "stomach pain", "வயிற்று வலி", "पेट दर्द", "पोटदुखी", "కడుపు నొప్పి", "ಹೊಟ್ಟೆ ನೋವು", "পেটে ব্যথা", "വയറുവേദന"],
    "dizziness": ["dizziness", "மயக்கம்", "चक्कर", "गरगरणे", "తల తిరగడం", "ತಲೆ ಸುತ್ತುವುದು", "মাথা ঘোরা", "തലകറക്കം"],
}


def extract_symptoms(text: str) -> dict:
    normalized = (text or "").casefold()
    found = []
    evidence = {}
    for code, phrases in SYMPTOMS.items():
        matches = [phrase for phrase in phrases if phrase.casefold() in normalized]
        if matches:
            found.append(code)
            evidence[code] = matches[:3]
    return {
        "symptoms": sorted(found),
        "evidence": evidence,
        "count": len(found),
        "extraction_status": "matched" if found else "no_known_symptom_match",
        "decision_support_only": True,
    }
