from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import BaseModel, Field, ConfigDict
from app.ai.asr.indic_conformer import transcribe
from app.ai.translation.indictrans2 import translate
from app.ai.triage.model import analyze_triage
from app.ai.triage.safety_rules import apply_safety
from app.referral.engine import recommend_referral, FACILITIES
from app.services.storage import (
    create_patient,
    get_patient,
    list_patients,
    store_encounter,
    get_patient_records,
    push_sync_operation,
    pull_sync_operations,
)

router = APIRouter()
SUPPORTED_LANGUAGES = ["en","as","bn","brx","doi","gu","hi","kn","gom","ks","mai","ml","mr","mni","ne","or","pa","sa","sat","snd","ta","te","ur"]

class TranslationRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    source_language: str = Field(min_length=2, max_length=10)
    target_language: str = Field(min_length=2, max_length=10)

class TriageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1, max_length=10000)
    language: str = "en"
    vitals: dict = Field(default_factory=dict)
    history: list = Field(default_factory=list)

class ReferralRequest(BaseModel):
    triage_level: str
    symptoms: list = Field(default_factory=list)
    location: str = ""
    specialty: str | None = None

class PatientRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    age: int | None = Field(default=None, ge=0, le=130)
    sex: str | None = Field(default=None, max_length=30)
    language: str = "en"

class EncounterRequest(BaseModel):
    patient_id: str
    original_language: str
    original_transcript: str = Field(default="", max_length=20000)
    normalized_data: dict = Field(default_factory=dict)

class SyncRequest(BaseModel):
    operation_id: str = Field(min_length=1, max_length=120)
    device_id: str = Field(min_length=1, max_length=120)
    entity_type: str = Field(min_length=1, max_length=80)
    entity_id: str | None = Field(default=None, max_length=120)
    payload: dict = Field(default_factory=dict)

@router.get("/languages")
def languages():
    return {"languages": SUPPORTED_LANGUAGES, "count": len(SUPPORTED_LANGUAGES)}

@router.post("/asr/transcribe")
async def asr_endpoint(audio_file: UploadFile = File(...), language: str = "hi"):
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(400, "Unsupported language")
    allowed = {"audio/wav","audio/x-wav","audio/mpeg","audio/mp4","audio/webm","audio/ogg"}
    if audio_file.content_type not in allowed:
        raise HTTPException(400, "Unsupported audio MIME type")
    audio = await audio_file.read()
    if len(audio) > 25 * 1024 * 1024:
        raise HTTPException(413, "Audio file too large")
    return transcribe(audio, language)

@router.post("/translation/translate")
def translation_endpoint(req: TranslationRequest):
    if req.source_language not in SUPPORTED_LANGUAGES or req.target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(400, "Unsupported language")
    return translate(req.text, req.source_language, req.target_language)

@router.post("/triage/analyze")
def triage_endpoint(req: TriageRequest):
    if req.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(400, "Unsupported language")
    ai = analyze_triage(req.text, req.language, req.vitals, req.history)
    return apply_safety(ai, req.text, req.vitals)

@router.post("/referral/recommend")
def referral_endpoint(req: ReferralRequest):
    return recommend_referral(req.triage_level, req.symptoms, req.location, req.specialty)

@router.get("/facilities")
def facilities():
    return FACILITIES

@router.post("/patients")
def create_patient_endpoint(req: PatientRequest):
    if req.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(400, "Unsupported language")
    return create_patient(req.model_dump())

@router.get("/patients")
def patients_endpoint(q: str = Query(default="", max_length=120)):
    return {"patients": list_patients(q)}

@router.get("/patients/{patient_id}")
def patient_endpoint(patient_id: str):
    patient = get_patient(patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")
    return patient

@router.post("/encounters")
def create_encounter(req: EncounterRequest):
    if not get_patient(req.patient_id):
        raise HTTPException(404, "Patient not found")
    return store_encounter(req.model_dump() | {"patient_id": req.patient_id})

@router.get("/patients/{patient_id}/records")
def records(patient_id: str):
    if not get_patient(patient_id):
        raise HTTPException(404, "Patient not found")
    return get_patient_records(patient_id)

@router.post("/consultations")
def consultation(payload: dict):
    if not payload.get("patient_id"):
        raise HTTPException(422, "patient_id is required")
    if not get_patient(payload["patient_id"]):
        raise HTTPException(404, "Patient not found")
    return store_encounter({"type":"consultation", "record_type":"consultation", **payload})

@router.post("/sync/push")
def sync_push(req: SyncRequest):
    return push_sync_operation(req.model_dump())

@router.get("/sync/pull")
def sync_pull(device_id: str | None = None):
    return {"operations": pull_sync_operations(device_id), "device_id": device_id}
