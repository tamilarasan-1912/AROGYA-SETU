from app.ai.symptoms.extractor import extract_symptoms


def test_symptom_extraction():
    result = extract_symptoms("fever and chest pain")
    assert "fever" in result["symptoms"]
    assert "chest_pain" in result["symptoms"]


def test_unknown_text_is_not_invented():
    result = extract_symptoms("general discomfort")
    assert result["symptoms"] == []
    assert result["extraction_status"] == "no_known_symptom_match"
