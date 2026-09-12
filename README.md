# AROGYASETU AI

Multilingual, offline-first rural healthcare orchestration prototype for India.

## Status
This branch contains the initial production-oriented skeleton: FastAPI API, React/Vite UI, centralized Indian-language configuration, Hugging Face model adapters, deterministic triage safety rules, referral engine, local persistence, offline sync queue, synthetic-data training scripts, tests and Docker scaffolding.

## Hugging Face models
- `ai4bharat/indic-conformer-600m-multilingual` — primary multilingual ASR. The Hub repository is gated.
- `ai4bharat/indictrans2-indic-indic-dist-320M` — Indic translation. The Hub repository is gated.
- `ai4bharat/indic-bert` — multilingual encoder baseline; not medically validated.
- `ai4bharat/indic-parler-tts-pretrained` — optional Indic TTS.

Set `HF_TOKEN` only through the environment. Never commit credentials.

## Synthetic training
Run `python scripts/generate_synthetic_data.py` to generate synthetic triage examples, then `python scripts/train_triage.py` with a configured Hugging Face token. This is demonstration training only and is not clinical validation.

## Safety
AI output is routing/decision support, not diagnosis. Deterministic emergency rules override model output, and low-confidence results are routed for human review.
