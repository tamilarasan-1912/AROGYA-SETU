from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from app.ai.asr.indic_conformer import transcribe
from app.ai.translation.indictrans2 import translate
from app.ai.triage.model import analyze_triage
from app.ai.triage.safety_rules import apply_safety
from app.referral.engine import recommend_referral
from app.services.storage import store_encounter, get_patient_records

router = APIRouter()

class TranslationRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    source_language: str
    target_language: str

class TriageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    language: str = "en"
    vitals: dict = {}
    history: list = []

class ReferralRequest(BaseModel):
    triage_level: str
    symptoms: list = []
    location: str = ""
    specialty: str | None = None

class PatientRequest(BaseModel):
    name: str
    age: int | None = None
    sex: str | None = None
    language: str = "en"

class EncounterRequest(BaseModel):
    patient_id: str
    original_language: str
    original_transcript: str
    normalized_data: dict

@router.get("/languages")
def languages():
    return ["en","as","bn","brx","doi","gu","hi","kn","gom","ks","mai","ml","mr","mni","ne","or","pa","sa","sat","snd","ta","te","ur"]

@router.post("/asr/transcribe")
async def asr_endpoint(audio_file: UploadFile = File(...), language: str = "hi"):
    if audio_file.content_type not in {"audio/wav","audio/x-wav","audio/mpeg","audio/mp4","audio/webm","audio/ogg"}:
        raise HTTPException(400, "Unsupported audio MIME type")
    audio = await audio_file.read()
    if len(audio) > 25 * 1024 * 1024:
        raise HTTPException(413, "Audio file too large")
    return transcribe(audio, language)

@router.post("/translation/translate")
def translation_endpoint(req: TranslationRequest):
    return translate(req.text, req.source_language, req.target_language)

@router.post("/triage/analyze")
def triage_endpoint(req: TriageRequest):
    ai = analyze_triage(req.text, req.language, req.vitals, req.history)
    return apply_safety(ai, req.text, req.vitals)

@router.post("/referral/recommend")
def referral_endpoint(req: ReferralRequest):
    return recommend_referral(req.triage_level, req.symptoms, req.location, req.specialty)

@router.post("/patients")
def create_patient(req: PatientRequest):
    return store_encounter({"type":"patient","patient":req.model_dump()})

@router.post("/encounters")
def create_encounter(req: EncounterRequest):
    return store_encounter(req.model_dump())

@router.get("/patients/{patient_id}/records")
def records(patient_id: str):
    return get_patient_records(patient_id)

@router.post("/consultations")
def consultation(payload: dict):
    return store_encounter({"type":"consultation", **payload})

@router.post("/sync/push")
def sync_push(payload: dict):
    return {"accepted": True, "operation_id": payload.get("operation_id"), "idempotent": True}

@router.get("/sync/pull")
def sync_pull(device_id: str | None = None):
    return {"operations": [], "device_id": device_id}

@router.get("/facilities")
def facilities():
    return [{"id":"demo-phc-01","name":"Demo Primary Health Centre","level":"PHC","telemedicine_available":True}]
