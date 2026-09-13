import os

os.environ.setdefault("USE_DATABASE", "false")

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_and_languages():
    health = client.get("/api/health")
    assert health.status_code == 200
    body = health.json()
    assert body["decision_support_only"] is True
    assert body["backend"] == "healthy"
    assert body["models"]["asr"]["model"] == "ai4bharat/indic-conformer-600m-multilingual"
    assert body["models"]["translation"]["model"] == "ai4bharat/indictrans2-indic-indic-dist-320M"
    assert body["models"]["triage"]["base_model"] == "ai4bharat/indic-bert"
    assert body["models"]["asr"]["loaded"] is False
    assert body["models"]["translation"]["loaded"] is False

    languages = client.get("/api/languages")
    assert languages.status_code == 200
    body = languages.json()
    assert body["count"] >= 22
    assert "ta" in body["languages"]
    assert "hi" in body["languages"]


def test_patient_encounter_and_records():
    patient_response = client.post(
        "/api/patients",
        json={"name": "Synthetic Demo Patient", "age": 35, "sex": "F", "language": "ta"},
    )
    assert patient_response.status_code == 200
    patient = patient_response.json()["patient"]
    patient_id = patient["id"]

    fetched = client.get(f"/api/patients/{patient_id}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == patient_id

    encounter = client.post(
        "/api/encounters",
        json={
            "patient_id": patient_id,
            "original_language": "ta",
            "original_transcript": "காய்ச்சல் மற்றும் இருமல்",
            "normalized_data": {"symptoms": ["fever", "cough"]},
        },
    )
    assert encounter.status_code == 200

    records = client.get(f"/api/patients/{patient_id}/records")
    assert records.status_code == 200
    assert len(records.json()["records"]) >= 1


def test_pipeline_emergency_safety_override():
    response = client.post(
        "/api/pipeline/analyze",
        json={"language": "en", "text": "The patient has severe chest pain and difficulty breathing."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision_support_only"] is True
    assert body["triage"]["triage_level"] == "LEVEL_1_EMERGENCY"
    assert body["triage"]["human_review_required"] is True
    assert body["triage"]["risk_level"] == "CRITICAL"
    assert "chest_pain" in body["triage"]["red_flags"]


def test_referral_endpoint():
    response = client.post(
        "/api/referral/recommend",
        json={"triage_level": "LEVEL_1_EMERGENCY", "symptoms": ["chest_pain"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["recommended_facility"]["level"] == "EMERGENCY"
    assert body["telemedicine_available"] is True


def test_consultation_session_lifecycle():
    patient_response = client.post(
        "/api/patients",
        json={"name": "Synthetic Consultation Patient", "age": 42, "language": "hi"},
    )
    assert patient_response.status_code == 200
    patient_id = patient_response.json()["patient"]["id"]

    created = client.post(
        "/api/consultations",
        json={"patient_id": patient_id, "clinician_name": "Demo Clinician"},
    )
    assert created.status_code == 200
    consultation = created.json()
    consultation_id = consultation["id"]
    assert consultation["room_id"].startswith("arogya-")
    assert consultation["status"] == "scheduled"

    active = client.patch(
        f"/api/consultations/{consultation_id}",
        json={"status": "active"},
    )
    assert active.status_code == 200
    assert active.json()["status"] == "active"
    assert active.json()["started_at"] is not None

    fetched = client.get(f"/api/consultations/{consultation_id}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == consultation_id

    completed = client.patch(
        f"/api/consultations/{consultation_id}",
        json={"status": "completed"},
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"


def test_sync_is_idempotent():
    payload = {
        "operation_id": "api-test-operation-001",
        "device_id": "api-test-device",
        "entity_type": "encounter",
        "entity_id": "encounter-001",
        "payload": {"status": "created"},
    }

    first = client.post("/api/sync/push", json=payload)
    second = client.post("/api/sync/push", json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["operation_id"] == second.json()["operation_id"]
    assert second.json()["idempotent"] is True

    pulled = client.get("/api/sync/pull", params={"device_id": "different-device"})
    assert pulled.status_code == 200
    operation_ids = [item["operation_id"] for item in pulled.json()["operations"]]
    assert operation_ids.count("api-test-operation-001") == 1
