from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

app = FastAPI(title="NLP Sentiment API")

# -------- Request Schema --------
class PredictionRequest(BaseModel):
    text: str
    model: str  # "base", "sequential", "full"

# -------- Globals --------
models = {}
tokenizers = {}
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

MODEL_PATHS = {
    "base": "dccuchile/bert-base-spanish-wwm-cased",  # remoto
    "sequential": "../fine_tuning/sequential-full-fine-tuning",
    "full": "../fine_tuning/spanish-bert-full-fine-tuning"
}

LABELS = {
    0: "NEG",
    1: "NEU",
    2: "POS"
}

# -------- Load models at startup --------
@app.on_event("startup")
def load_models():
    for name, path in MODEL_PATHS.items():
        tokenizer = AutoTokenizer.from_pretrained(path)
        model = AutoModelForSequenceClassification.from_pretrained(path)
        model.to(device)
        model.eval()

        tokenizers[name] = tokenizer
        models[name] = model

    print("Models loaded successfully.")

# -------- Prediction endpoint --------
@app.post("/predict")
def predict(request: PredictionRequest):

    if request.model not in models:
        raise HTTPException(status_code=400, detail="Invalid model name")

    tokenizer = tokenizers[request.model]
    model = models[request.model]

    inputs = tokenizer(
        request.text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        predicted_class = torch.argmax(probs, dim=1).item()

    return {
        "model_used": request.model,
        "prediction": LABELS[predicted_class],
        "confidence": float(probs[0][predicted_class])
    }
