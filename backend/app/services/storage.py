import uuid

# Prototype persistence boundary. Replace with SQLAlchemy/PostgreSQL repository in deployment.
_PATIENTS = {}
_RECORDS = {}

def store_encounter(payload):
    pid = payload.get("patient_id") or payload.get("patient", {}).get("id") or str(uuid.uuid4())
    _PATIENTS.setdefault(pid, payload.get("patient", {}))
    _RECORDS.setdefault(pid, []).append({"id":str(uuid.uuid4()), **payload})
    return {"patient_id":pid,"record_id":_RECORDS[pid][-1]["id"],"stored":True}

def get_patient_records(patient_id):
    return {"patient_id":patient_id,"records":_RECORDS.get(patient_id, [])}
