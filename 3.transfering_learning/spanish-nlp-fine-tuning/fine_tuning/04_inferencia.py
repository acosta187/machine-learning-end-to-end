"""
SCRIPT 4: Inferencia con múltiples modelos (Jerga + Base)
==========================================================
Permite probar:

- Modelo full_ftuning
- Modelo sequential_ftuning
- Modelo base FiniteAutomata

Uso:

    python 04_inferencia.py
    python 04_inferencia.py --model sequential_ftuning
    python 04_inferencia.py --model finiteautomata "Ese servicio estuvo bacán pe"
"""

import sys
import argparse
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ================================================================
# CONFIGURACIÓN
# ================================================================

AVAILABLE_MODELS = {
    "full_ftuning": "./spanish-bert-full-fine-tuning",
    "sequential_ftuning": "./sequential-full-fine-tuning",
    "finiteautomata": "finiteautomata/beto-sentiment-analysis",
}

DEFAULT_MODEL = "sequential_ftuning"

MAX_LENGTH = 96
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

ID2LABEL = {0: "NEGATIVE", 1: "NEUTRAL", 2: "POSITIVE"}
LABEL_EMOJI = {"POSITIVE": "😊", "NEGATIVE": "😞", "NEUTRAL": "😐"}

# ================================================================
# CARGAR MODELO
# ================================================================

def cargar_modelo(model_key):

    model_path = AVAILABLE_MODELS[model_key]

    print("\n" + "=" * 60)
    print(f"📦 Modelo seleccionado : {model_key}")
    print(f"📂 Ruta / ID           : {model_path}")
    print("=" * 60)

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    modelo = AutoModelForSequenceClassification.from_pretrained(model_path)

    modelo.to(DEVICE)
    modelo.eval()

    print(f"✅ Cargado en dispositivo: {DEVICE}")
    print(f"📏 Tamaño vocabulario     : {len(tokenizer)} tokens\n")

    return tokenizer, modelo

# ================================================================
# PREDICCIÓN
# ================================================================

def predecir(texto, modelo, tokenizer):

    encoding = tokenizer(
        texto,
        truncation=True,
        padding="max_length",
        max_length=MAX_LENGTH,
        return_tensors="pt"
    )

    encoding = {k: v.to(DEVICE) for k, v in encoding.items()}

    with torch.no_grad():
        outputs = modelo(**encoding)

    probs = torch.softmax(outputs.logits, dim=-1)[0].cpu().numpy()
    pred_int = int(np.argmax(probs))
    pred_str = ID2LABEL[pred_int]

    return {
        "texto": texto,
        "label_int": pred_int,
        "label_str": pred_str,
        "emoji": LABEL_EMOJI[pred_str],
        "confianza": float(probs[pred_int]),
        "probabilidades": {
            "NEGATIVE": float(probs[0]),
            "NEUTRAL": float(probs[1]),
            "POSITIVE": float(probs[2]),
        }
    }

# ================================================================
# IMPRESIÓN BONITA
# ================================================================

def imprimir_resultado(r):

    print(f"\n📝 Texto     : {r['texto']}")
    print(
        f"🎯 Resultado : {r['emoji']} {r['label_str']} "
        f"(confianza: {r['confianza']:.1%})"
    )
    print(
        f"📊 Probs     : "
        f"NEG={r['probabilidades']['NEGATIVE']:.3f} | "
        f"NEU={r['probabilidades']['NEUTRAL']:.3f} | "
        f"POS={r['probabilidades']['POSITIVE']:.3f}"
    )

# ================================================================
# DEMO + INTERACTIVO
# ================================================================

def demo(tokenizer, modelo):

    ejemplos = [
        "Ese servicio estuvo bacán pe",
        "Qué palta ese delivery, llegó tarde y maleado",
        "Mi causa me dijo que mañana cambian el horario",
        "El técnico fue un mostro, lo arregló al toque",
        "Todo piola por acá, sin novedades",
        "Ese pata es bien sapo, cargoso total",
        "Chévere la nueva app, funciona de pelos",
        "Qué roche más grande, me llamaron la atención",
    ]

    print("\n" + "=" * 65)
    print("  Demo de Inferencia")
    print("=" * 65)

    for texto in ejemplos:
        r = predecir(texto, modelo, tokenizer)
        imprimir_resultado(r)

    print("\n" + "=" * 65)
    print("  Modo interactivo (escribe 'salir' para terminar)")
    print("=" * 65)

    while True:
        texto = input("\n📝 Ingresa un texto: ").strip()
        if texto.lower() in ("salir", "exit", "quit", ""):
            break
        r = predecir(texto, modelo, tokenizer)
        imprimir_resultado(r)

# ================================================================
# MAIN
# ================================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        choices=AVAILABLE_MODELS.keys(),
        help="Modelo a usar"
    )
    parser.add_argument(
        "texto",
        nargs="*",
        help="Texto para clasificar"
    )

    args = parser.parse_args()

    tokenizer, modelo = cargar_modelo(args.model)

    if args.texto:
        texto = " ".join(args.texto)
        r = predecir(texto, modelo, tokenizer)
        imprimir_resultado(r)
    else:
        demo(tokenizer, modelo)
