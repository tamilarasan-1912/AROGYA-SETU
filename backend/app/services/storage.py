import json
import os
import uuid
from datetime import datetime

USE_DATABASE = os.getenv("USE_DATABASE", "false").lower() == "true"

_PATIENTS: dict[str, dict] = {}
_RECORDS: dict[str, list[dict]] = {}
_SYNC_OPERATIONS: dict[str, dict] = {}


def _now() -> str:
    return datetime.utcnow().isoformat()


def create_patient(payload: dict) -> dict:
    patient_id = payload.get("id") or str(uuid.uuid4())
    patient = {"id": patient_id, "name": payload.get("name", ""), "age": payload.get("age"), "sex": payload.get("sex"), "language": payload.get("language", "en"), "created_at": payload.get("created_at") or _now()}
    if USE_DATABASE:
        try:
            from app.db import db_session
            from app.models import Patient
            with db_session() as db:
                existing = db.get(Patient, patient_id)
                if existing:
                    return {"patient": patient, "created": False, "storage": "postgresql"}
                db.add(Patient(id=patient_id, name=patient["name"], age=patient["age"], sex=patient["sex"], language=patient["language"]))
            return {"patient": patient, "created": True, "storage": "postgresql"}
        except Exception as exc:
            return {"patient": patient, "created": False, "stored": False, "requires_database": True, "error": str(exc)}
    _PATIENTS[patient_id] = patient
    return {"patient": patient, "created": True, "storage": "memory-demo"}


def list_patients(query: str = "") -> list[dict]:
    if USE_DATABASE:
        try:
            from app.db import db_session
            from app.models import Patient
            with db_session() as db:
                rows = db.query(Patient).order_by(Patient.created_at.desc()).all()
                q = query.strip().lower()
                if q:
                    rows = [r for r in rows if q in r.name.lower() or q in r.id.lower()]
                return [{"id": r.id, "name": r.name, "age": r.age, "sex": r.sex, "language": r.language, "created_at": r.created_at.isoformat() if r.created_at else None} for r in rows]
        except Exception:
            pass
    rows = list(_PATIENTS.values())
    q = query.strip().lower()
    if q:
        rows = [p for p in rows if q in p.get("name", "").lower() or q in p.get("id", "").lower()]
    return rows


def get_patient(patient_id: str) -> dict | None:
    if USE_DATABASE:
        try:
            from app.db import db_session
            from app.models import Patient
            with db_session() as db:
                p = db.get(Patient, patient_id)
                if p:
                    return {"id": p.id, "name": p.name, "age": p.age, "sex": p.sex, "language": p.language, "created_at": p.created_at.isoformat() if p.created_at else None}
        except Exception:
            pass
    return _PATIENTS.get(patient_id)


def _db_store_encounter(payload: dict) -> dict:
    from app.db import db_session
    from app.models import Encounter, HealthRecord, Patient
    patient_data = payload.get("patient", {})
    pid = payload.get("patient_id") or patient_data.get("id") or str(uuid.uuid4())
    with db_session() as db:
        patient = db.get(Patient, pid)
        if patient is None:
            patient = Patient(id=pid, name=patient_data.get("name", "Demo Patient"), age=patient_data.get("age"), sex=patient_data.get("sex"), language=patient_data.get("language", "en"))
            db.add(patient)
            db.flush()
        encounter = Encounter(patient_id=pid, original_language=payload.get("original_language", payload.get("language", patient.language)), original_transcript=payload.get("original_transcript", payload.get("transcript", "")), normalized_data=json.dumps(payload.get("normalized_data", {}), ensure_ascii=False))
        db.add(encounter)
        db.flush()
        record = HealthRecord(patient_id=pid, record_type=payload.get("record_type", "encounter"), payload=json.dumps(payload, ensure_ascii=False))
        db.add(record)
        db.flush()
        return {"patient_id": pid, "record_id": record.id, "encounter_id": encounter.id, "stored": True, "storage": "postgresql"}


def store_encounter(payload: dict) -> dict:
    if USE_DATABASE:
        try:
            return _db_store_encounter(payload)
        except Exception as exc:
            return {"stored": False, "requires_database": True, "error": str(exc)}
    pid = payload.get("patient_id") or payload.get("patient", {}).get("id") or str(uuid.uuid4())
    if payload.get("patient"):
        _PATIENTS.setdefault(pid, {"id": pid, **payload["patient"]})
    record = {"id": str(uuid.uuid4()), "created_at": _now(), **payload}
    _RECORDS.setdefault(pid, []).append(record)
    return {"patient_id": pid, "record_id": record["id"], "stored": True, "storage": "memory-demo"}


def _db_get_patient_records(patient_id: str) -> dict:
    from app.db import db_session
    from app.models import HealthRecord
    with db_session() as db:
        records = db.query(HealthRecord).filter(HealthRecord.patient_id == patient_id).order_by(HealthRecord.created_at.desc()).all()
        return {"patient_id": patient_id, "records": [{"id": r.id, "record_type": r.record_type, "payload": json.loads(r.payload), "created_at": r.created_at.isoformat() if r.created_at else None} for r in records]}


def get_patient_records(patient_id: str) -> dict:
    if USE_DATABASE:
        try:
            return _db_get_patient_records(patient_id)
        except Exception as exc:
            return {"patient_id": patient_id, "records": [], "requires_database": True, "error": str(exc)}
    return {"patient_id": patient_id, "records": _RECORDS.get(patient_id, []), "storage": "memory-demo"}


def push_sync_operation(operation: dict) -> dict:
    operation_id = operation.get("operation_id")
    if not operation_id:
        raise ValueError("operation_id is required")
    if USE_DATABASE:
        try:
            from app.db import db_session
            from app.models import SyncOperation
            with db_session() as db:
                existing = db.query(SyncOperation).filter(SyncOperation.operation_id == operation_id).first()
                if existing:
                    return {"accepted": True, "operation_id": operation_id, "idempotent": True, "status": existing.status}
                db.add(SyncOperation(operation_id=operation_id, device_id=operation.get("device_id", "unknown"), entity_type=operation.get("entity_type", "unknown"), entity_id=operation.get("entity_id"), payload=json.dumps(operation.get("payload", {}), ensure_ascii=False), status="accepted"))
            return {"accepted": True, "operation_id": operation_id, "idempotent": False, "status": "accepted"}
        except Exception as exc:
            return {"accepted": False, "operation_id": operation_id, "error": str(exc), "requires_database": True}
    if operation_id in _SYNC_OPERATIONS:
        return {"accepted": True, "operation_id": operation_id, "idempotent": True, "status": _SYNC_OPERATIONS[operation_id]["status"]}
    _SYNC_OPERATIONS[operation_id] = {**operation, "status": "accepted", "received_at": _now()}
    return {"accepted": True, "operation_id": operation_id, "idempotent": False, "status": "accepted"}


def pull_sync_operations(device_id: str | None = None) -> list[dict]:
    if USE_DATABASE:
        try:
            from app.db import db_session
            from app.models import SyncOperation
            with db_session() as db:
                rows = db.query(SyncOperation).order_by(SyncOperation.created_at.asc()).all()
                return [{"operation_id": r.operation_id, "device_id": r.device_id, "entity_type": r.entity_type, "entity_id": r.entity_id, "payload": json.loads(r.payload), "status": r.status, "created_at": r.created_at.isoformat() if r.created_at else None} for r in rows if not device_id or r.device_id != device_id]
        except Exception:
            pass
    return [op for op in _SYNC_OPERATIONS.values() if not device_id or op.get("device_id") != device_id]
