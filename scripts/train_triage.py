"""Fine-tune IndicBERT on SYNTHETIC demo data only.

This produces a hackathon prototype classifier. It is NOT clinical validation
and must not be used to make autonomous medical decisions.
"""
import csv
import os
from pathlib import Path

from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)

MODEL = "ai4bharat/indic-bert"
LABELS = [
    "LEVEL_1_EMERGENCY",
    "LEVEL_2_URGENT",
    "LEVEL_3_PRIMARY_CARE",
    "LEVEL_4_ROUTINE",
]
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic_triage_generated.csv"
OUTPUT = ROOT / "models" / "triage-synthetic"

rows = list(csv.DictReader(DATA.open(encoding="utf-8")))
if len(rows) < 100:
    raise RuntimeError("Synthetic dataset is unexpectedly small. Run generate_synthetic_data.py first.")

train_rows, test_rows = train_test_split(
    rows,
    test_size=0.2,
    random_state=42,
    stratify=[row["label"] for row in rows],
)


def make_dataset(records):
    return Dataset.from_list(
        [{"text": row["text"], "language": row["language"], "labels": LABELS.index(row["label"])} for row in records]
    )


tokenizer = AutoTokenizer.from_pretrained(MODEL, token=os.getenv("HF_TOKEN"))


def encode(batch):
    return tokenizer(batch["text"], truncation=True, max_length=128)


train_ds = make_dataset(train_rows).map(encode, batched=True)
test_ds = make_dataset(test_rows).map(encode, batched=True)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL,
    num_labels=len(LABELS),
    id2label={i: label for i, label in enumerate(LABELS)},
    label2id={label: i for i, label in enumerate(LABELS)},
    token=os.getenv("HF_TOKEN"),
)


def metrics(prediction):
    predictions = prediction.predictions.argmax(axis=-1)
    labels = prediction.label_ids
    return {
        "accuracy": accuracy_score(labels, predictions),
        "macro_f1": f1_score(labels, predictions, average="macro"),
    }


args = TrainingArguments(
    output_dir=str(OUTPUT),
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    learning_rate=2e-5,
    weight_decay=0.01,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="macro_f1",
    greater_is_better=True,
    report_to="none",
    seed=42,
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_ds,
    eval_dataset=test_ds,
    tokenizer=tokenizer,
    data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
    compute_metrics=metrics,
)
trainer.train()
results = trainer.evaluate()
trainer.save_model(str(OUTPUT))
tokenizer.save_pretrained(str(OUTPUT))

print("Synthetic prototype training complete")
print(f"Examples: {len(rows)} | train: {len(train_rows)} | test: {len(test_rows)}")
print(f"Evaluation: {results}")
print(f"Saved model: {OUTPUT}")
print("WARNING: synthetic-only model; not clinically validated.")
