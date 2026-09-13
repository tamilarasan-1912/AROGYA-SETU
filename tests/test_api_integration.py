import os

os.environ.setdefault("USE_DATABASE", "false")

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_and_languages():
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["decision_support_only"] is True

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
    patient = patient_response.json()
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
    assert len(records.json()) >= 1


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

    pulled = client.get("/api/sync/pull", params={"device_id": "different-device"})
    assert pulled.status_code == 200
    operation_ids = [item["operation_id"] for item in pulled.json()["operations"]]
    assert operation_ids.count("api-test-operation-001") == 1
