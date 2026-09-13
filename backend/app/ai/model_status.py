import os
from pathlib import Path

ASR_MODEL_ID = "ai4bharat/indic-conformer-600m-multilingual"
TRANSLATION_MODEL_ID = "ai4bharat/indictrans2-indic-indic-dist-320M"
TRIAGE_BASE_MODEL_ID = "ai4bharat/indic-bert"
DEFAULT_TRIAGE_PATH = "models/triage-synthetic"


def _hf_model_status(model_id: str) -> dict:
    token_configured = bool(os.getenv("HF_TOKEN", "").strip())
    return {
        "model": model_id,
        "status": "configured_gated_model" if token_configured else "gated_model_requires_token",
        "token_configured": token_configured,
        "loaded": False,
    }


def _local_triage_status() -> dict:
    path_value = os.getenv("TRIAGE_MODEL_PATH", DEFAULT_TRIAGE_PATH)
    path = Path(path_value)
    if not path.is_dir():
        return {
            "base_model": TRIAGE_BASE_MODEL_ID,
            "local_model_path": str(path),
            "status": "base_model_fallback",
            "loaded": False,
        }

    required = [path / "config.json"]
    has_weights = any(
        candidate.exists()
        for candidate in (
            path / "model.safetensors",
            path / "pytorch_model.bin",
            path / "model.safetensors.index.json",
            path / "pytorch_model.bin.index.json",
        )
    )
    if all(item.exists() for item in required) and has_weights:
        return {
            "base_model": TRIAGE_BASE_MODEL_ID,
            "local_model_path": str(path),
            "status": "local_model_ready",
            "loaded": False,
        }

    return {
        "base_model": TRIAGE_BASE_MODEL_ID,
        "local_model_path": str(path),
        "status": "local_model_incomplete",
        "loaded": False,
    }


def get_model_status() -> dict:
    return {
        "asr": _hf_model_status(ASR_MODEL_ID),
        "translation": _hf_model_status(TRANSLATION_MODEL_ID),
        "triage": _local_triage_status(),
        "note": "Status is a readiness/configuration check; models are not downloaded or loaded by the health endpoint.",
    }
