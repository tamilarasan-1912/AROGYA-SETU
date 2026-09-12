import io, os
from functools import lru_cache

MODEL_ID = os.getenv("ASR_MODEL", "ai4bharat/indic-conformer-600m-multilingual")

@lru_cache(maxsize=1)
def _load():
    from transformers import AutoModel, AutoProcessor
    processor = AutoProcessor.from_pretrained(MODEL_ID, token=os.getenv("HF_TOKEN"), trust_remote_code=True)
    model = AutoModel.from_pretrained(MODEL_ID, token=os.getenv("HF_TOKEN"), trust_remote_code=True)
    return processor, model

def transcribe(audio_bytes: bytes, language: str):
    try:
        import soundfile as sf
        import numpy as np
        audio, sr = sf.read(io.BytesIO(audio_bytes))
        if audio.ndim > 1: audio = audio.mean(axis=1)
        if sr != 16000:
            import librosa
            audio = librosa.resample(np.asarray(audio, dtype=np.float32), orig_sr=sr, target_sr=16000)
        processor, model = _load()
        inputs = processor(audio, sampling_rate=16000, return_tensors="pt", language=language)
        outputs = model.generate(**inputs)
        text = processor.batch_decode(outputs, skip_special_tokens=True)[0]
        return {"language":language,"transcript":text,"confidence":None,"duration":len(audio)/16000,"model":MODEL_ID}
    except Exception as exc:
        return {"language":language,"transcript":None,"confidence":None,"duration":None,"model":MODEL_ID,"error":str(exc),"requires_model_setup":True}
