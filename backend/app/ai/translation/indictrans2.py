import os
from functools import lru_cache

MODEL_ID = os.getenv("TRANSLATION_MODEL", "ai4bharat/indictrans2-indic-indic-dist-320M")

# IndicTrans2 uses FLORES-style script-aware language tags.
LANGUAGE_TAGS = {
    "as": "asm_Beng", "bn": "ben_Beng", "brx": "brx_Deva", "doi": "doi_Deva",
    "gom": "gom_Deva", "gu": "guj_Gujr", "hi": "hin_Deva", "kn": "kan_Knda",
    "ks": "kas_Arab", "mai": "mai_Deva", "ml": "mal_Mlym", "mr": "mar_Deva",
    "mni": "mni_Mtei", "ne": "npi_Deva", "or": "ory_Orya", "pa": "pan_Guru",
    "sa": "san_Deva", "sat": "sat_Olck", "snd": "snd_Deva", "ta": "tam_Taml",
    "te": "tel_Telu", "ur": "urd_Arab",
}

@lru_cache(maxsize=1)
def _load():
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    from IndicTransToolkit.processor import IndicProcessor
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=os.getenv("HF_TOKEN"), trust_remote_code=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID, token=os.getenv("HF_TOKEN"), trust_remote_code=True).to(device)
    model.eval()
    processor = IndicProcessor(inference=True)
    return tokenizer, model, processor, device


def translate(text: str, source_language: str, target_language: str):
    if source_language == target_language:
        return {"source_language": source_language, "target_language": target_language, "source_text": text, "translated_text": text, "model": MODEL_ID}
    if source_language not in LANGUAGE_TAGS or target_language not in LANGUAGE_TAGS:
        return {"source_language": source_language, "target_language": target_language, "source_text": text, "translated_text": None, "model": MODEL_ID, "error": "IndicTrans2 endpoint supports the 22 Indic languages; English is not a supported target/source for this model.", "requires_model_setup": False}
    try:
        import torch
        tokenizer, model, processor, device = _load()
        src_lang = LANGUAGE_TAGS[source_language]
        tgt_lang = LANGUAGE_TAGS[target_language]
        batch = processor.preprocess_batch([text], src_lang=src_lang, tgt_lang=tgt_lang)
        inputs = tokenizer(batch, padding=True, truncation=True, return_tensors="pt").to(device)
        with torch.inference_mode():
            generated = model.generate(**inputs, max_length=256, num_beams=5, num_return_sequences=1)
        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
        translated = processor.postprocess_batch(decoded, lang=tgt_lang)[0]
        return {"source_language": source_language, "target_language": target_language, "source_text": text, "translated_text": translated, "model": MODEL_ID, "device": device}
    except Exception as exc:
        return {"source_language": source_language, "target_language": target_language, "source_text": text, "translated_text": None, "model": MODEL_ID, "error": str(exc), "requires_model_setup": True}
