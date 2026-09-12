import csv, random
from pathlib import Path
random.seed(42)
langs={'en':['fever','cough','headache','vomiting','chest pain and difficulty breathing'],'hi':['बुखार','खांसी','सिरदर्द','उल्टी','सीने में दर्द और सांस लेने में कठिनाई'],'mr':['ताप','खोकला','डोकेदुखी','उलटी','छातीत दुखणे आणि श्वास घेण्यास त्रास'],'ta':['காய்ச்சல்','இருமல்','தலைவலி','வாந்தி','மார்பு வலி மற்றும் மூச்சுத்திணறல்'],'te':['జ్వరం','దగ్గు','తలనొప్పి','వాంతులు','ఛాతీ నొప్పి మరియు శ్వాసలో ఇబ్బంది']}
rows=[]
for _ in range(500):
    lang=random.choice(list(langs)); symptom=random.choice(langs[lang]); emergency='chest' in symptom or 'छाती' in symptom or 'மார்பு' in symptom or 'ఛాతీ' in symptom
    label='LEVEL_1_EMERGENCY' if emergency else random.choice(['LEVEL_3_PRIMARY_CARE','LEVEL_4_ROUTINE'])
    rows.append({'text':symptom,'language':lang,'label':label})
out=Path(__file__).resolve().parents[1]/'data'/'synthetic_triage_generated.csv'; out.parent.mkdir(exist_ok=True)
with out.open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['text','language','label']); w.writeheader(); w.writerows(rows)
print(out)