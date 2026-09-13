import os

os.environ["USE_DATABASE"] = "false"

from app.services.storage import create_patient, get_patient, get_patient_records, push_sync_operation


def test_patient_crud_demo_storage():
    result = create_patient({"name": "Synthetic Patient", "age": 42, "sex": "F", "language": "ta"})
    assert result["created"] is True
    patient_id = result["patient"]["id"]
    assert get_patient(patient_id)["name"] == "Synthetic Patient"


def test_sync_is_idempotent():
    operation = {"operation_id": "test-op-001", "device_id": "test-device", "entity_type": "patient", "entity_id": "p1", "payload": {"name": "Synthetic"}}
    first = push_sync_operation(operation)
    second = push_sync_operation(operation)
    assert first["accepted"] is True
    assert first["idempotent"] is False
    assert second["accepted"] is True
    assert second["idempotent"] is True


def test_patient_records_empty_for_new_patient():
    result = create_patient({"name": "Records Patient", "language": "hi"})
    assert get_patient_records(result["patient"]["id"])["records"] == []
