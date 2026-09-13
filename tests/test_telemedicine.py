import os

os.environ.setdefault("USE_DATABASE", "false")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_telemedicine_websocket_join_and_signal():
    with client.websocket_connect("/api/telemedicine/ws/demo-room/asha-1") as websocket:
        joined = websocket.receive_json()
        assert joined["type"] == "joined"
        assert joined["room_id"] == "demo-room"
        assert joined["peer_id"] == "asha-1"
        assert joined["demo_mode"] is True


def test_telemedicine_consultation_lifecycle():
    patient = client.post(
        "/api/patients",
        json={"name": "Synthetic Telemedicine Patient", "age": 42, "sex": "F", "language": "ta"},
    ).json()["patient"]

    created = client.post(
        "/api/consultations",
        json={"patient_id": patient["id"], "clinician_name": "Demo Clinician"},
    )
    assert created.status_code == 200
    consultation = created.json()
    assert consultation["room_id"]
    assert consultation["status"] == "scheduled"

    active = client.patch(
        f"/api/consultations/{consultation['id']}",
        json={"status": "active"},
    )
    assert active.status_code == 200
    assert active.json()["status"] == "active"

    completed = client.patch(
        f"/api/consultations/{consultation['id']}",
        json={"status": "completed"},
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
