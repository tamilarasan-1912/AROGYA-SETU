import os
from functools import lru_cache

MODEL_ID = os.getenv("TRANSLATION_MODEL", "ai4bharat/indictrans2-indic-indic-dist-320M")

@lru_cache(maxsize=1)
def _load():
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=os.getenv("HF_TOKEN"), trust_remote_code=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID, token=os.getenv("HF_TOKEN"), trust_remote_code=True)
    return tok, model

def translate(text: str, source_language: str, target_language: str):
    if source_language == target_language:
        return {"source_language":source_language,"target_language":target_language,"source_text":text,"translated_text":text,"model":MODEL_ID}
    try:
        tok, model = _load()
        prompt = f"{source_language} {target_language}: {text}"
        inputs = tok(prompt, return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=256)
        translated = tok.batch_decode(out, skip_special_tokens=True)[0]
        return {"source_language":source_language,"target_language":target_language,"source_text":text,"translated_text":translated,"model":MODEL_ID}
    except Exception as exc:
        return {"source_language":source_language,"target_language":target_language,"source_text":text,"translated_text":None,"model":MODEL_ID,"error":str(exc),"requires_model_setup":True}
