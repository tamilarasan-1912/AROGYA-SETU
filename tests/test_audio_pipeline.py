from fastapi.testclient import TestClient

from app.main import app
import app.api.routes as routes

client = TestClient(app)


def test_audio_pipeline_chains_asr_to_clinical_flow(monkeypatch):
    monkeypatch.setattr(
        routes,
        "transcribe",
        lambda audio, language: {
            "language": language,
            "transcript": "எனக்கு மார்பு வலி உள்ளது",
            "confidence": None,
            "duration": 1.0,
            "model": "test-asr",
        },
    )

    response = client.post(
        "/api/pipeline/analyze-audio",
        files={"audio_file": ("sample.wav", b"RIFFTEST", "audio/wav")},
        data={"language": "ta"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["transcript"] == "எனக்கு மார்பு வலி உள்ளது"
    assert body["asr"]["model"] == "test-asr"
    assert body["triage"]["triage_level"] == "LEVEL_1_EMERGENCY"
    assert body["triage"]["model_status"] == "safety_override"
    assert body["pipeline"] == [
        "audio_ingestion",
        "asr",
        "symptom_extraction",
        "triage",
        "safety",
        "referral",
        "recording",
    ]


def test_audio_pipeline_rejects_invalid_mime():
    response = client.post(
        "/api/pipeline/analyze-audio",
        files={"audio_file": ("sample.txt", b"hello", "text/plain")},
        data={"language": "ta"},
    )
    assert response.status_code == 400
