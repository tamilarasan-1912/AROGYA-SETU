import json
import os
import uuid
from datetime import datetime

USE_DATABASE = os.getenv("USE_DATABASE", "false").lower() == "true"

# In-memory fallback keeps the hackathon demo runnable without PostgreSQL.
_PATIENTS: dict[str, dict] = {}
_RECORDS: dict[str, list[dict]] = {}


def _db_store_encounter(payload: dict) -> dict:
    from app.db import db_session
    from app.models import Encounter, HealthRecord, Patient

    patient_data = payload.get("patient", {})
    pid = payload.get("patient_id") or patient_data.get("id") or str(uuid.uuid4())
    with db_session() as db:
        patient = db.get(Patient, pid)
        if patient is None:
            patient = Patient(
                id=pid,
                name=patient_data.get("name", "Demo Patient"),
                age=patient_data.get("age"),
                sex=patient_data.get("sex"),
                language=patient_data.get("language", "en"),
            )
            db.add(patient)

        encounter = Encounter(
            patient_id=pid,
            original_language=payload.get("language", patient.language),
            original_transcript=payload.get("transcript", ""),
            normalized_data=json.dumps(payload.get("normalized_data", {}), ensure_ascii=False),
        )
        db.add(encounter)
        db.flush()

        record = HealthRecord(
            patient_id=pid,
            record_type="encounter",
            payload=json.dumps(payload, ensure_ascii=False),
        )
        db.add(record)
        db.flush()
        return {"patient_id": pid, "record_id": record.id, "encounter_id": encounter.id, "stored": True}


def store_encounter(payload: dict) -> dict:
    if USE_DATABASE:
        try:
            return _db_store_encounter(payload)
        except Exception as exc:
            # Do not break a field demo when the database is unavailable.
            return {
                "stored": False,
                "requires_database": True,
                "error": str(exc),
            }

    pid = payload.get("patient_id") or payload.get("patient", {}).get("id") or str(uuid.uuid4())
    _PATIENTS.setdefault(pid, payload.get("patient", {}))
    record = {"id": str(uuid.uuid4()), "created_at": datetime.utcnow().isoformat(), **payload}
    _RECORDS.setdefault(pid, []).append(record)
    return {"patient_id": pid, "record_id": record["id"], "stored": True, "storage": "memory-demo"}


def _db_get_patient_records(patient_id: str) -> dict:
    from app.db import db_session
    from app.models import HealthRecord

    with db_session() as db:
        records = (
            db.query(HealthRecord)
            .filter(HealthRecord.patient_id == patient_id)
            .order_by(HealthRecord.created_at.desc())
            .all()
        )
        return {
            "patient_id": patient_id,
            "records": [
                {
                    "id": r.id,
                    "record_type": r.record_type,
                    "payload": json.loads(r.payload),
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in records
            ],
        }


def get_patient_records(patient_id: str) -> dict:
    if USE_DATABASE:
        try:
            return _db_get_patient_records(patient_id)
        except Exception as exc:
            return {"patient_id": patient_id, "records": [], "requires_database": True, "error": str(exc)}
    return {"patient_id": patient_id, "records": _RECORDS.get(patient_id, []), "storage": "memory-demo"}
