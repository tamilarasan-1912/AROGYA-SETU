import pytest

from app.ai.pipeline import run_clinical_decision_pipeline
from app.ai.triage.safety_rules import apply_safety
from app.ai.triage.model import analyze_triage


@pytest.mark.parametrize(
    "language,text,expected_flag",
    [
        ("ta", "எனக்கு மார்பு வலி உள்ளது", "chest_pain"),
        ("hi", "मुझे सीने में दर्द है", "chest_pain"),
        ("mr", "मला छातीत दुखणे आहे", "chest_pain"),
        ("te", "నాకు ఛాతి నొప్పి ఉంది", "chest_pain"),
        ("kn", "ನನಗೆ ಎದೆ ನೋವು ಇದೆ", "chest_pain"),
    ],
)
def test_multilingual_emergency_safety_override(language, text, expected_flag):
    result = apply_safety(analyze_triage(text, language, {}, []), text, {})
    assert result["triage_level"] == "LEVEL_1_EMERGENCY"
    assert result["risk_level"] == "CRITICAL"
    assert result["risk_score"] == 100
    assert result["human_review_required"] is True
    assert expected_flag in result["red_flags"]
    assert result["safety_checked"] is True


@pytest.mark.parametrize(
    "language,text",
    [
        ("ta", "எனக்கு காய்ச்சல் மற்றும் இருமல் உள்ளது"),
        ("hi", "मुझे बुखार और खांसी है"),
        ("mr", "मला ताप आणि खोकला आहे"),
        ("te", "నాకు జ్వరం మరియు దగ్గు ఉంది"),
        ("kn", "ನನಗೆ ಜ್ವರ ಮತ್ತು ಕೆಮ್ಮು ಇದೆ"),
    ],
)
def test_multilingual_pipeline_extracts_symptoms(language, text):
    result = run_clinical_decision_pipeline(text, language)
    codes = set(result["symptoms"]["symptoms"])
    assert "fever" in codes
    assert "cough" in codes
    assert result["decision_support_only"] is True
    assert result["triage"]["safety_checked"] is True
    assert "referral" in result["pipeline"]
