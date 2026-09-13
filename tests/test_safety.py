from app.ai.triage.safety_rules import apply_safety


def test_emergency_red_flag_overrides_ai_result():
    result = apply_safety({"triage_level": "LEVEL_4_ROUTINE", "confidence": 0.99, "red_flags": []}, "patient has chest pain", {})
    assert result["triage_level"] == "LEVEL_1_EMERGENCY"
    assert result["risk_level"] == "CRITICAL"
    assert result["risk_score"] == 100
    assert result["human_review_required"] is True


def test_low_confidence_requires_human_review():
    result = apply_safety({"triage_level": "LEVEL_3_PRIMARY_CARE", "confidence": 0.2, "red_flags": []}, "mild fever", {})
    assert result["human_review_required"] is True
    assert "human review" in result["recommended_action"].lower()
