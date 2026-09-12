import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(title="AROGYASETU AI", version="0.1.0")
origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api")

@app.get("/api/health")
def health():
    return {
        "backend": "healthy",
        "database": "configured" if os.getenv("DATABASE_URL") else "prototype-default",
        "asr_model": "ai4bharat/indic-conformer-600m-multilingual",
        "translation_model": "ai4bharat/indictrans2-indic-indic-dist-320M",
        "triage_model": os.getenv("TRIAGE_MODEL", "models/triage-synthetic (fallback: ai4bharat/indic-bert)"),
    }
