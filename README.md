# AROGYASETU AI

Multilingual, offline-first rural healthcare orchestration prototype for India.

## Current implementation status
This branch now contains an executable product skeleton with:
- FastAPI backend and React/Vite frontend.
- Centralized Indian-language configuration.
- Hugging Face model adapters for ASR, Indic translation and synthetic triage training.
- Audio-to-clinical pipeline: audio ingestion → IndicConformer ASR → symptom extraction → triage → deterministic safety override → referral → encounter recording.
- Deterministic multilingual emergency safety rules for the core demo languages.
- Synthetic referral directory and telemedicine WebSocket signaling prototype.
- Patient, encounter, consultation, health-record and idempotent sync APIs.
- Dexie offline queue with online-triggered push/pull reconciliation.
- Backend pytest coverage and GitHub Actions CI.
- Docker/PostgreSQL scaffolding for the production-oriented architecture.

## Hugging Face models
- `ai4bharat/indic-conformer-600m-multilingual` — primary multilingual ASR. The Hub repository is gated.
- `ai4bharat/indictrans2-indic-indic-dist-320M` — Indic translation. The Hub repository is gated.
- `ai4bharat/indic-bert` — multilingual encoder baseline; not medically validated.
- `ai4bharat/indic-parler-tts-pretrained` — optional Indic TTS.

IndicConformer inference follows the model's documented CTC interface and its language identifiers; the product maps `gom` → `kok` and `snd` → `sd` for ASR compatibility. citeturn1search0turn1search5

Set `HF_TOKEN` only through the environment. Never commit credentials.

## Synthetic training
Run `python scripts/generate_synthetic_data.py` to generate synthetic triage examples, then `python scripts/train_triage.py` with a configured Hugging Face token. This is demonstration training only and is not clinical validation.

## Key API flow
- `POST /api/asr/transcribe` — speech-to-text.
- `POST /api/pipeline/analyze-audio` — complete audio-to-decision-support demo path.
- `POST /api/pipeline/analyze` — transcript-to-decision-support path.
- `POST /api/translation/translate` — Indic translation.
- `POST /api/triage/analyze` — triage plus deterministic safety layer.
- `POST /api/referral/recommend` — referral recommendation.
- `POST /api/consultations` + `PATCH /api/consultations/{id}` — telemedicine lifecycle.
- `WS /api/telemedicine/ws/{room_id}/{peer_id}` — prototype WebRTC signaling channel.
- `POST /api/sync/push` + `GET /api/sync/pull` — idempotent offline synchronization.

## Testing
FastAPI's `TestClient` supports both HTTP endpoints and WebSocket sessions, so the repository tests cover the API and telemedicine signaling without requiring a live socket server. citeturn0search0turn0search1

From the repository root:

```bash
cd backend
pip install -r requirements.txt
PYTHONPATH=. USE_DATABASE=false pytest -q ../tests
```

The CI workflow is `.github/workflows/backend-tests.yml`.

## Safety
AI output is routing/decision support, not diagnosis. Deterministic emergency rules override model output, and low-confidence results are routed for human review.
