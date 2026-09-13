import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.ai.model_status import get_model_status

app = FastAPI(title="AROGYASETU AI", version="0.3.1")

cors_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(router, prefix="/api")


@app.on_event("startup")
def startup() -> None:
    if os.getenv("USE_DATABASE", "false").lower() != "true":
        return
    try:
        from app.db import init_db
        init_db()
    except Exception as exc:
        print(f"Database initialization skipped: {exc}")


@app.get("/api/health")
def health():
    return {
        "backend": "healthy",
        "database": "enabled" if os.getenv("USE_DATABASE", "false").lower() == "true" else "demo-memory",
        "models": get_model_status(),
        "decision_support_only": True,
    }
