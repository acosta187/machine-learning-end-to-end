# ==============================================================
# GENERADOR DE DATASET SINTÉTICO – JERGA PERUANA
# ==============================================================

import csv
import random
import os

random.seed(42)

# ==============================================================
# CONFIGURACIÓN
# ==============================================================

SAMPLES_POR_CLASE = 320
RUTA_SALIDA = "sintetic_data/dataset_sintetico.csv"

LABEL_MAP = {
    "NEGATIVE": 0,
    "NEUTRAL": 1,
    "POSITIVE": 2
}

# ==============================================================
# VARIACIÓN LINGÜÍSTICA (AUMENTO DE DATA)
# ==============================================================

SUFIJOS = ["", " pe", " oe", " mano"]
PUNTUACION = ["", ".", "!", "!!"]

def variar_texto(texto: str) -> list:
    variantes = set()

    for suf in SUFIJOS:
        for p in PUNTUACION:
            t = texto + suf + p
            variantes.add(t)

            if random.random() < 0.3:
                variantes.add(t.capitalize())

    return list(variantes)

# ==============================================================
# SLOTS (VOCABULARIO)
# ==============================================================

SLOTS = {
    "servicio": ["el servicio", "la atención", "la experiencia", "el trato"],
    "producto": ["el producto", "la comida", "el resultado"],
    "lugar": ["este lugar", "ese sitio", "el local"],

    # POSITIVOS
    "adj_pos": [
        "bacán",
        "chévere",
        "pulento",
        "de pelos",
        "mostro",
        "bacán y de primera",
        "chévere y firme",
        "pulento, de campeonato",
        "bacanazo total"
    ],

    # NEGATIVOS
    "adj_neg": [
        "pésimo",
        "horrible",
        "malísimo",
        "fatal",
        "terrible"
    ],

    "sust_neg": [
        "roche",
        "palta",
        "roche total",
        "palta terrible",
        "un roche bien feo"
    ]
}

# ==============================================================
# PLANTILLAS
# ==============================================================

PLANTILLAS_POS = [
    "{servicio} estuvo {adj_pos}",
    "{producto} salió {adj_pos}",
    "{lugar} está {adj_pos}",
    "todo fue {adj_pos}",
    "{servicio} fue {adj_pos}"
]

PLANTILLAS_NEG = [
    "{servicio} fue {adj_neg}",
    "{producto} fue un {sust_neg}",
    "todo fue un {sust_neg}",
    "{lugar} estuvo {adj_neg}",
    "{servicio} terminó en {sust_neg}"
]

PLANTILLAS_NEU = [
    "{servicio} estuvo normal",
    "{producto} fue regular",
    "{lugar} está bien",
    "todo estuvo ok",
    "nada fuera de lo común"
]

# ==============================================================
# FUNCIONES
# ==============================================================

def rellenar_plantilla(plantilla: str, slots: dict) -> str:
    texto = plantilla
    for key in slots:
        if "{" + key + "}" in texto:
            texto = texto.replace("{" + key + "}", random.choice(slots[key]))
    return texto

def generar_ejemplos_clase(plantillas, slots, n, label_str):
    ejemplos = []
    intentos = 0
    max_intentos = n * 20

    while len(ejemplos) < n and intentos < max_intentos:
        plantilla = random.choice(plantillas)
        base = rellenar_plantilla(plantilla, slots)

        for texto in variar_texto(base):
            if len(ejemplos) >= n:
                break

            ejemplos.append({
                "texto": texto,
                "label_str": label_str,
                "label_int": LABEL_MAP[label_str]
            })

        intentos += 1

    return ejemplos[:n]

# ==============================================================
# GENERAR DATASET
# ==============================================================

def generar_dataset(n_por_clase=SAMPLES_POR_CLASE):
    print("🔹 Generando dataset sintético...")

    data = []
    data += generar_ejemplos_clase(PLANTILLAS_POS, SLOTS, n_por_clase, "POSITIVE")
    data += generar_ejemplos_clase(PLANTILLAS_NEU, SLOTS, n_por_clase, "NEUTRAL")
    data += generar_ejemplos_clase(PLANTILLAS_NEG, SLOTS, n_por_clase, "NEGATIVE")

    random.shuffle(data)

    os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)

    with open(RUTA_SALIDA, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["texto", "label_str", "label_int"]
        )
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ Dataset generado: {RUTA_SALIDA}")
    print(f"   Total ejemplos : {len(data)}")
    print(f"   POSITIVE (2)   : {sum(d['label_int']==2 for d in data)}")
    print(f"   NEUTRAL  (1)   : {sum(d['label_int']==1 for d in data)}")
    print(f"   NEGATIVE (0)   : {sum(d['label_int']==0 for d in data)}")

# ==============================================================
# MAIN
# ==============================================================

if __name__ == "__main__":
    generar_dataset()

