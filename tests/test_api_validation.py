import os

os.environ.setdefault("USE_DATABASE", "false")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_patient_validation_rejects_negative_age():
    response = client.post("/api/patients", json={"name": "Invalid", "age": -1, "language": "ta"})
    assert response.status_code == 422


def test_patient_validation_rejects_unknown_language():
    response = client.post("/api/patients", json={"name": "Invalid", "language": "xx"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported language"


def test_triage_rejects_unknown_language():
    response = client.post("/api/triage/analyze", json={"text": "fever", "language": "xx"})
    assert response.status_code == 400


def test_pipeline_rejects_unknown_language():
    response = client.post("/api/pipeline/analyze", json={"text": "fever", "language": "xx"})
    assert response.status_code == 400


def test_missing_patient_blocks_consultation():
    response = client.post("/api/consultations", json={"patient_id": "does-not-exist"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found"


def test_consultation_rejects_invalid_status():
    patient = client.post("/api/patients", json={"name": "Validation Demo", "language": "ta"})
    assert patient.status_code == 200
    patient_id = patient.json()["patient"]["id"]
    created = client.post("/api/consultations", json={"patient_id": patient_id})
    assert created.status_code == 200
    response = client.patch(f"/api/consultations/{created.json()['id']}", json={"status": "unknown"})
    assert response.status_code == 422


def test_audio_upload_size_limit():
    response = client.post(
        "/api/asr/transcribe",
        files={"audio_file": ("large.wav", b"x" * (25 * 1024 * 1024 + 1), "audio/wav")},
        data={"language": "ta"},
    )
    assert response.status_code == 413
