# ==========================================================
# 03_finetune_beto.py
# Fine-tuning BETO Sentiment + Jerga Peruana
# ==========================================================

import os
import random
import numpy as np
import pandas as pd
import torch

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)

# ==========================================================
# CONFIGURACIÓN
# ==========================================================

CONFIG = {
    # 🔥 Ahora usamos el modelo ya entrenado en sentimiento
    "model_name": "finiteautomata/beto-sentiment-analysis",

    # ---- Dataset ----
    "dataset_path": "./sintetic_data/dataset_sintetico.csv",
    "text_col": "texto",
    "label_col": "label_int",
    "num_labels": 3,

    # ---- Glosario ----
    "glosario_csv": "./sintetic_data/glosario_jerga_peruana.csv",
    "glosario_col": "termino",

    # ---- Training (ajustado) ----
    "epochs": 4,
    "batch_size": 16,
    "learning_rate": 2e-5,
    "max_length": 96,
    "test_size": 0.2,
    "seed": 42,

    # ---- Output ----
    "output_dir": "./sequential-full-fine-tuning",
}

# ==========================================================
# SEED
# ==========================================================

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

# ==========================================================
# CARGAR GLOSARIO
# ==========================================================

def cargar_glosario(config):
    df = pd.read_csv(config["glosario_csv"])
    tokens = (
        df[config["glosario_col"]]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )
    return tokens

# ==========================================================
# PREPARAR TOKENIZER + MODELO
# ==========================================================

def preparar_modelo(config):

    print("🔹 Cargando tokenizer base...")
    tokenizer = AutoTokenizer.from_pretrained(config["model_name"])

    # ---- Añadir jerga ----
    tokens_glosario = cargar_glosario(config)

    tokens_nuevos = [
        t for t in tokens_glosario
        if tokenizer.convert_tokens_to_ids(t) == tokenizer.unk_token_id
    ]

    if tokens_nuevos:
        tokenizer.add_tokens(tokens_nuevos)
        print(f"🆕 Tokens nuevos añadidos: {len(tokens_nuevos)}")
    else:
        print("ℹ️ Todos los tokens del glosario ya existen.")

    print("🔹 Cargando modelo base de sentimiento...")
    model = AutoModelForSequenceClassification.from_pretrained(
        config["model_name"],
        num_labels=config["num_labels"],
        ignore_mismatched_sizes=True  # 🔥 clave
    )

    if tokens_nuevos:
        model.resize_token_embeddings(len(tokenizer))
        print(f"📏 Embeddings redimensionados: {len(tokenizer)} tokens")

    return tokenizer, model

# ==========================================================
# TOKENIZACIÓN
# ==========================================================

def tokenizar_dataset(dataset, tokenizer, config):

    def tokenize_fn(batch):
        return tokenizer(
            batch[config["text_col"]],
            padding="max_length",
            truncation=True,
            max_length=config["max_length"]
        )

    return dataset.map(tokenize_fn, batched=True)

# ==========================================================
# MÉTRICAS
# ==========================================================

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=1)

    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average="macro", zero_division=0
    )
    acc = accuracy_score(labels, preds)

    return {
        "accuracy": acc,
        "f1_macro": f1,
        "precision": precision,
        "recall": recall
    }

# ==========================================================
# ENTRENAMIENTO
# ==========================================================

def entrenar():

    set_seed(CONFIG["seed"])

    print("🔹 Cargando dataset...")
    df = pd.read_csv(CONFIG["dataset_path"])

    train_df, val_df = train_test_split(
        df,
        test_size=CONFIG["test_size"],
        random_state=CONFIG["seed"],
        stratify=df[CONFIG["label_col"]]
    )

    train_dataset = Dataset.from_pandas(train_df)
    val_dataset   = Dataset.from_pandas(val_df)

    tokenizer, model = preparar_modelo(CONFIG)

    train_dataset = tokenizar_dataset(train_dataset, tokenizer, CONFIG)
    val_dataset   = tokenizar_dataset(val_dataset, tokenizer, CONFIG)

    train_dataset = train_dataset.rename_column(CONFIG["label_col"], "labels")
    val_dataset   = val_dataset.rename_column(CONFIG["label_col"], "labels")

    train_dataset.set_format(
        "torch",
        columns=["input_ids", "attention_mask", "labels"]
    )
    val_dataset.set_format(
        "torch",
        columns=["input_ids", "attention_mask", "labels"]
    )

    training_args = TrainingArguments(
        output_dir=CONFIG["output_dir"],
        num_train_epochs=CONFIG["epochs"],
        per_device_train_batch_size=CONFIG["batch_size"],
        per_device_eval_batch_size=CONFIG["batch_size"],
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=CONFIG["learning_rate"],
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        logging_steps=10,
        save_total_limit=2,
        seed=CONFIG["seed"],
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        tokenizer=tokenizer
    )

    print("🚀 Iniciando entrenamiento...")
    trainer.train()

    print("💾 Guardando modelo y tokenizer...")
    trainer.save_model(CONFIG["output_dir"])
    tokenizer.save_pretrained(CONFIG["output_dir"])

    print("✅ Entrenamiento completado correctamente.")

# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":
    entrenar()

