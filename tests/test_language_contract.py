from fastapi.testclient import TestClient

from app.main import app
from app.api.routes import SUPPORTED_LANGUAGES
from app.ai.asr.indic_conformer import LANGUAGE_ALIASES as ASR_LANGUAGE_ALIASES


client = TestClient(app)

EXPECTED_APPLICATION_LANGUAGES = {
    "en", "as", "bn", "brx", "doi", "gu", "hi", "kn", "gom", "ks", "mai",
    "ml", "mr", "mni", "ne", "or", "pa", "sa", "sat", "sd", "ta", "te", "ur",
}


def test_api_exposes_complete_canonical_language_set():
    response = client.get("/api/languages")
    assert response.status_code == 200
    body = response.json()
    assert set(body["languages"]) == EXPECTED_APPLICATION_LANGUAGES
    assert body["count"] == len(EXPECTED_APPLICATION_LANGUAGES)
    assert set(SUPPORTED_LANGUAGES) == EXPECTED_APPLICATION_LANGUAGES


def test_sindhi_uses_public_sd_code():
    assert "sd" in SUPPORTED_LANGUAGES
    assert "snd" not in SUPPORTED_LANGUAGES


def test_sindhi_is_mapped_only_at_model_adapter_boundary():
    assert ASR_LANGUAGE_ALIASES.get("sd") == "snd"


def test_unknown_language_is_rejected_consistently():
    triage = client.post("/api/triage/analyze", json={"text": "fever", "language": "xx"})
    pipeline = client.post("/api/pipeline/analyze", json={"text": "fever", "language": "xx"})
    patient = client.post("/api/patients", json={"name": "Synthetic Patient", "language": "xx"})
    assert triage.status_code == 400
    assert pipeline.status_code == 400
    assert patient.status_code == 400
