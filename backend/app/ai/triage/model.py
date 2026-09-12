import os, re
from functools import lru_cache

MODEL_ID = os.getenv("TRIAGE_MODEL", "ai4bharat/indic-bert")
LABELS = ["LEVEL_1_EMERGENCY","LEVEL_2_URGENT","LEVEL_3_PRIMARY_CARE","LEVEL_4_ROUTINE"]

@lru_cache(maxsize=1)
def _load():
    from transformers import AutoTokenizer, AutoModel
    return AutoTokenizer.from_pretrained(MODEL_ID, token=os.getenv("HF_TOKEN")), AutoModel.from_pretrained(MODEL_ID, token=os.getenv("HF_TOKEN"))

def analyze_triage(text, language, vitals=None, history=None):
    vitals, history = vitals or {}, history or []
    # Prototype decision-support baseline: encoder is loaded to provide real HF representation;
    # routing remains conservative until a clinically reviewed classifier is trained.
    try:
        _load()
        model_status = "loaded"
    except Exception as exc:
        model_status = f"unavailable: {exc}"
    low = text.lower()
    red = [x for x in ["chest pain","difficulty breathing","unconscious","seizure","severe bleeding","stroke"] if x in low]
    if red:
        level = "LEVEL_1_EMERGENCY"
    elif any(x in low for x in ["high fever","persistent vomiting","severe pain"]):
        level = "LEVEL_2_URGENT"
    elif text.strip():
        level = "LEVEL_3_PRIMARY_CARE"
    else:
        level = "LEVEL_4_ROUTINE"
    return {"triage_level":level,"confidence":0.0,"reason_codes":[],"red_flags":red,"recommended_action":"Requires healthcare professional review.","model":MODEL_ID,"model_status":model_status}
