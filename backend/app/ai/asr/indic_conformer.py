import io
import os
from functools import lru_cache

import torch

MODEL_ID = os.getenv("ASR_MODEL", "ai4bharat/indic-conformer-600m-multilingual")

# Product language codes -> IndicConformer language codes.
# The product keeps "gom" and "snd" for the broader language configuration,
# while IndicConformer exposes Konkani as "kok" and Sindhi as "sd".
MODEL_LANGUAGE = {"gom": "kok", "snd": "sd"}

@lru_cache(maxsize=1)
def _load():
    from transformers import AutoModel
    model = AutoModel.from_pretrained(
        MODEL_ID,
        token=os.getenv("HF_TOKEN"),
        trust_remote_code=True,
    )
    model.eval()
    return model


def transcribe(audio_bytes: bytes, language: str):
    try:
        import soundfile as sf
        import numpy as np

        audio, sr = sf.read(io.BytesIO(audio_bytes))
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        audio = np.asarray(audio, dtype=np.float32)
        if sr != 16000:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)

        model = _load()
        wav = torch.from_numpy(audio).unsqueeze(0)
        model_language = MODEL_LANGUAGE.get(language, language)
        with torch.inference_mode():
            transcription = model(wav, model_language, "ctc")
        if isinstance(transcription, (list, tuple)):
            transcription = transcription[0]
        text = str(transcription).strip()
        return {
            "language": language,
            "model_language": model_language,
            "transcript": text,
            "confidence": None,
            "duration": len(audio) / 16000,
            "model": MODEL_ID,
            "decoder": "ctc",
        }
    except Exception as exc:
        return {
            "language": language,
            "transcript": None,
            "confidence": None,
            "duration": None,
            "model": MODEL_ID,
            "error": str(exc),
            "requires_model_setup": True,
        }
