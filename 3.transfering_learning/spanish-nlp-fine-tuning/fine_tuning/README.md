# Fine-Tuning BETO para Sentimientos en Español Peruano
## Guía completa del proyecto

---

## Estructura del proyecto

```
proyecto/
├── 01_generar_glosario.py        # Genera el glosario de jerga
├── 02_generar_dataset.py         # Genera dataset sintético
├── 03_finetune_beto.py           # Pipeline de fine-tuning
├── 04_inferencia.py              # Inferencia con modelo guardado
├── glosario_jerga_peruana.csv    # Glosario generado
├── glosario_jerga_peruana.xlsx   # Glosario con formato visual
├── dataset_sintetico.csv         # Dataset generado
└── modelo_beto_peruano/          # Modelo entrenado (se crea al entrenar)
    ├── pytorch_model.bin
    ├── config.json
    ├── tokenizer files...
    └── metadata_entrenamiento.json
```

Los modelos entrenados se encuntran en el siguiente link:
https://drive.google.com/drive/folders/1NJWz6YDGsM1nOj8ge4SCZTJlVM7Fbdo7?usp=sharing

sequential-full-fine-tuning.zip y spanish-bert-full-fine-tuning.zip
---

## Instalación de dependencias

```bash
pip install torch transformers scikit-learn pandas openpyxl matplotlib seaborn
```

---

## Orden de ejecución

### Paso 1 — Generar glosario
```bash
python 01_generar_glosario.py
```
Genera `glosario_jerga_peruana.csv` y `glosario_jerga_peruana.xlsx`

### Paso 2 — Generar dataset sintético
```bash
python 02_generar_dataset.py
```
Genera `dataset_sintetico.csv` con 360 ejemplos balanceados (120 por clase)

### Paso 3 — Fine-tuning
```bash
python 03_finetune_beto.py
```
- Entrena el modelo
- Guarda visualizaciones en `modelo_beto_peruano/`
- Guarda métricas en `metadata_entrenamiento.json`

### Paso 4 — Inferencia
```bash
# Demo interactivo
python 04_inferencia.py

# Predicción directa
python 04_inferencia.py "Ese servicio estuvo bacán pe"
```

---

## Configuración clave en 03_finetune_beto.py

### Cambiar el modelo base
```python
# Para datasets pequeños (<2000 ejemplos): usar modelo ya especializado
"model_name": "finiteautomata/beto-sentiment-analysis"

# Para datasets grandes (>5000 ejemplos reales): partir desde base
"model_name": "dccuchile/bert-base-spanish-wwm-uncased"
```

### Ajustar hiperparámetros según tamaño de dataset

| Dataset       | LR     | Épocas | Batch |
|--------------|--------|--------|-------|
| <500 ejemplos | 1e-5   | 3      | 8     |
| 500–2000      | 2e-5   | 4      | 16    |
| 2000–10000    | 3e-5   | 5      | 32    |
| >10000        | 3e-5   | 6      | 32    |

### Añadir tu propio CSV de datos reales
1. Tu CSV debe tener columnas: `texto` (str) y `label_int` (int: 0, 1 o 2)
2. Cambia en CONFIG:
```python
"data_csv": "mi_dataset_real.csv"
```
3. Para combinar sintético + real:
```python
import pandas as pd
df_real      = pd.read_csv("mi_dataset_real.csv")
df_sintetico = pd.read_csv("dataset_sintetico.csv")
df_combinado = pd.concat([df_real, df_sintetico]).sample(frac=1, random_state=42)
df_combinado.to_csv("dataset_combinado.csv", index=False)
# Luego usar "data_csv": "dataset_combinado.csv"
```

---

## Mapeo de labels (no modificar)

| Label int | Label string | Significado   |
|-----------|-------------|---------------|
| 0         | NEGATIVE    | Sentimiento negativo |
| 1         | NEUTRAL     | Sentimiento neutro   |
| 2         | POSITIVE    | Sentimiento positivo |

---

## Líneas que NO debes cambiar

En `03_finetune_beto.py`, estas líneas son críticas y no deben modificarse:

```python
# Labels — el modelo base usa estos exactos valores
"num_labels": 3,
"id2label":   {0: "NEGATIVE", 1: "NEUTRAL", 2: "POSITIVE"},
"label2id":   {"NEGATIVE": 0, "NEUTRAL": 1, "POSITIVE": 2},

# Crítico para compatibilidad con beto-sentiment-analysis
ignore_mismatched_sizes=True

# Redimensionar embeddings DESPUÉS de añadir tokens
modelo.resize_token_embeddings(len(tokenizer))
```

---

## Métricas a monitorear

Más allá del accuracy, prioriza en este orden:

1. **F1 Macro** — trata todas las clases igual (crucial con clases desbalanceadas)
2. **F1 por clase** — identifica qué clase aprende peor (usualmente NEUTRAL)
3. **Val Loss vs Train Loss** — detecta sobreajuste
4. **Accuracy en jerga** — métrica específica del proyecto peruano (función `validar_aprendizaje_jerga`)

---

## Señales de sobreajuste

- Train loss bajando + Val loss subiendo → reducir épocas o aumentar weight_decay
- F1 en test << F1 en validación → necesitas más datos reales
- Accuracy en jerga < 60% → el modelo no aprendió la jerga, revisar tokenización

---

## Notas académicas

- **Modelo base**: `finiteautomata/beto-sentiment-analysis` fue entrenado con tweets en español.
  Al hacer fine-tuning sobre él, aprovechamos los pesos de sentimientos ya aprendidos.
- **ignore_mismatched_sizes=True**: necesario porque el modelo original puede tener 
  configuración de labels diferente (POS/NEG vs POS/NEU/NEG).
- **Tokens de jerga**: BERT tokeniza "bacán" como subwords desconocidos. Al añadirlos 
  explícitamente al vocabulario, el modelo puede aprender representaciones directas para ellos.
