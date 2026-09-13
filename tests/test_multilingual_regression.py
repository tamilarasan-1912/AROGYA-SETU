from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

MANDATORY_LANGUAGES = ["ta", "hi", "mr", "te", "kn"]
CHEST_PAIN = {
    "ta": "எனக்கு நெஞ்சு வலி மற்றும் மூச்சுத்திணறல் உள்ளது",
    "hi": "मुझे सीने में दर्द और सांस लेने में कठिनाई है",
    "mr": "मला छातीत दुखत आहे आणि श्वास घेण्यास त्रास होत आहे",
    "te": "నాకు ఛాతి నొప్పి మరియు శ్వాస తీసుకోవడంలో ఇబ్బంది ఉంది",
    "kn": "ನನಗೆ ಎದೆ ನೋವು ಮತ್ತು ಉಸಿರಾಟದ ತೊಂದರೆ ఉంది",
}


def test_languages_endpoint_contains_required_demo_languages():
    response = client.get("/api/languages")
    assert response.status_code == 200
    languages = response.json()["languages"]
    for language in MANDATORY_LANGUAGES:
        assert language in languages


def test_emergency_safety_override_across_required_languages():
    for language in MANDATORY_LANGUAGES:
        response = client.post("/api/triage/analyze", json={"text": CHEST_PAIN[language], "language": language})
        assert response.status_code == 200
        body = response.json()
        assert body["triage_level"] == "LEVEL_1_EMERGENCY"
        assert body["risk_level"] == "CRITICAL"
        assert body["safety_override"] is True
        assert body["human_review_required"] is True


def test_pipeline_accepts_patient_id_for_demo_recording():
    patient = client.post("/api/patients", json={"name": "Regression Demo", "age": 42, "sex": "other", "language": "ta"})
    assert patient.status_code == 200
    patient_id = (patient.json().get("patient") or patient.json())["id"]
    response = client.post("/api/pipeline/analyze", json={"text": CHEST_PAIN["ta"], "language": "ta", "patient_id": patient_id})
    assert response.status_code == 200
    assert response.json()["encounter"]["patient_id"] == patient_id


def test_consultation_lifecycle_contract():
    patient = client.post("/api/patients", json={"name": "Consult Demo", "language": "hi"})
    patient_id = (patient.json().get("patient") or patient.json())["id"]
    created = client.post("/api/consultations", json={"patient_id": patient_id})
    assert created.status_code == 200
    consultation = created.json()
    assert consultation["room_id"]
    assert consultation["status"] == "scheduled"
    active = client.patch(f"/api/consultations/{consultation['id']}", json={"status": "active"})
    assert active.status_code == 200
    assert active.json()["status"] == "active"
    completed = client.patch(f"/api/consultations/{consultation['id']}", json={"status": "completed"})
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
