from fastapi import APIRouter, UploadFile, File, HTTPException, Query, WebSocket, Form
from pydantic import BaseModel, Field, ConfigDict
from app.ai.asr.indic_conformer import transcribe
from app.ai.translation.indictrans2 import translate
from app.ai.triage.model import analyze_triage
from app.ai.triage.safety_rules import apply_safety
from app.ai.pipeline import run_clinical_decision_pipeline
from app.referral.engine import recommend_referral, FACILITIES
from app.telemedicine.signaling import signaling_session
from app.services.storage import (
    create_patient, get_patient, list_patients, store_encounter, get_patient_records,
    create_consultation, get_consultation, update_consultation,
    push_sync_operation, pull_sync_operations,
)

router = APIRouter()
# Public/API language code is the canonical ISO-style application code.
# Sindhi is `sd`; model adapters translate it to the Indic model's `snd` code.
SUPPORTED_LANGUAGES = ["en","as","bn","brx","doi","gu","hi","kn","gom","ks","mai","ml","mr","mni","ne","or","pa","sa","sat","sd","ta","te","ur"]
AUDIO_MIME_TYPES = {"audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp4", "audio/webm", "audio/ogg"}

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

class PipelineRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20000)
    language: str = "en"
    patient_id: str | None = None
    vitals: dict = Field(default_factory=dict)
    history: list = Field(default_factory=list)
    location: str = ""
    specialty: str | None = None

class ReferralRequest(BaseModel):
    triage_level: str
    symptoms: list = Field(default_factory=list)
    location: str = ""
    specialty: str | None = None
