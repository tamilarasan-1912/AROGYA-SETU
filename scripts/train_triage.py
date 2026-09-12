"""Fine-tune IndicBERT on SYNTHETIC demo data only. This is NOT clinical validation."""
import csv, os
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from sklearn.model_selection import train_test_split
MODEL='ai4bharat/indic-bert'
LABELS=['LEVEL_1_EMERGENCY','LEVEL_2_URGENT','LEVEL_3_PRIMARY_CARE','LEVEL_4_ROUTINE']
rows=list(csv.DictReader(open('data/synthetic_triage_generated.csv',encoding='utf-8')))
train,test=train_test_split(rows,test_size=.2,random_state=42,stratify=[r['label'] for r in rows])
def make(rs): return Dataset.from_list([{**r,'labels':LABELS.index(r['label'])} for r in rs])
tok=AutoTokenizer.from_pretrained(MODEL,token=os.getenv('HF_TOKEN'))
def enc(batch): return tok(batch['text'],truncation=True,padding='max_length',max_length=128)
tr=make(train).map(enc,batched=True); te=make(test).map(enc,batched=True)
model=AutoModelForSequenceClassification.from_pretrained(MODEL,num_labels=len(LABELS),token=os.getenv('HF_TOKEN'))
args=TrainingArguments(output_dir='models/triage-synthetic',num_train_epochs=2,per_device_train_batch_size=8,learning_rate=2e-5,report_to='none',save_strategy='epoch')
Trainer(model=model,args=args,train_dataset=tr,eval_dataset=te).train()
model.save_pretrained('models/triage-synthetic'); tok.save_pretrained('models/triage-synthetic')
print('Saved synthetic-only prototype classifier. Do not represent as clinically validated.')