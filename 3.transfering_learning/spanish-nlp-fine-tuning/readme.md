# 🧠 Spanish NLP — Sentiment Fine-Tuning

> Análisis de sentimiento en español con Transformers (BERT), fine-tuning avanzado y despliegue full-stack mediante FastAPI + Streamlit.

**Autor:** Carlos

---

## 📌 Tabla de Contenidos

1. [Arquitectura General](#arquitectura-general)
2. [Configuración de Entornos](#configuración-de-entornos)
3. [Entrenamiento de Modelos](#entrenamiento-de-modelos)
4. [Teoría: Full vs Sequential Fine-Tuning](#teoría-full-vs-sequential-fine-tuning)
5. [Lanzar la API (FastAPI)](#lanzar-la-api-fastapi)
6. [Lanzar el Frontend (Streamlit)](#lanzar-el-frontend-streamlit)
7. [Flujo Completo de Ejecución](#flujo-completo-de-ejecución)
8. [Estructura del Proyecto](#estructura-del-proyecto)
9. [Buenas Prácticas](#buenas-prácticas)
10. [Mejoras Futuras](#mejoras-futuras)

---

## 🏗️ Arquitectura General

El sistema integra tres capas bien diferenciadas: un modelo base preentrenado en español, dos variantes de fine-tuning, y una interfaz completa de despliegue.

```
Usuario → Streamlit (Frontend) → FastAPI (Backend) → Modelo BERT → Respuesta
```

| Componente | Descripción |
|---|---|
| Modelo base | `dccuchile/bert-base-spanish-wwm-cased` |
| Fine-tuning 1 | Sequential Fine-Tuning |
| Fine-tuning 2 | Full Fine-Tuning |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |

---

## ⚙️ Configuración de Entornos

Se usan entornos separados para aislar dependencias entre entrenamiento, backend e inferencia.

### 🔹 Entorno de Entrenamiento

```bash
conda create -n transformers_env python=3.9
conda activate transformers_env

pip install torch torchvision torchaudio
pip install transformers datasets scikit-learn pandas numpy accelerate
```

> **GPU (opcional):** Verifica compatibilidad con `nvidia-smi` antes de instalar la versión CUDA de PyTorch.

---

### 🔹 Entorno para API (FastAPI)

```bash
conda activate transformers_env

pip install fastapi uvicorn torch transformers
```

---

### 🔹 Entorno para Frontend (Streamlit)

```bash
conda create -n streamlit_env python=3.11
conda activate streamlit_env

pip install streamlit requests
```

---

## 🤖 Entrenamiento de Modelos

Se entrenaron tres variantes para comparar rendimiento:

| Estrategia | Descripción |
|------------|------------|
| **Modelo Base** | Sin fine-tuning para la tarea de sentimiento. Posee conocimiento lingüístico general del español, pero la capa clasificadora está inicializada aleatoriamente. |
| **Full Fine-Tuning** | Todos los pesos del modelo (incluyendo las capas Transformer y el clasificador) se actualizan directamente sobre el dataset objetivo. |
| **Sequential Fine-Tuning** | El modelo se entrena en dos fases: primero en una tarea intermedia (o dominio relacionado) y luego se vuelve a ajustar sobre la tarea final de sentimiento. |

---

## 📚 Teoría: Full vs Sequential Fine-Tuning

### Full Fine-Tuning

Se parte del modelo base preentrenado y se ajustan **todos los parámetros** directamente sobre el dataset de sentimiento.

**Ventajas:**
- Máxima adaptación a la tarea específica
- Mayor potencial de rendimiento final
- Aprende vocabulario y estilo del dominio objetivo

**Desventajas:**
- Mayor riesgo de *overfitting*
- Puede producir *catastrophic forgetting* del conocimiento general
- Más costoso computacionalmente

---

### Sequential Fine-Tuning

Entrenamiento en **dos o más etapas**: primero en un corpus de dominio cercano (e.g., reseñas generales) y luego en el dataset final de sentimiento.

**Ventajas:**
- Transferencia progresiva y controlada
- Reduce el riesgo de olvidar conocimiento previo
- Mejor generalización entre dominios

**Desventajas:**
- Mayor complejidad de implementación
- Requiere múltiples datasets de calidad
- Tiempo total de entrenamiento más alto

---

### ⚖️ Comparativa

| Aspecto | Full Fine-Tuning | Sequential Fine-Tuning |
|---|---|---|
| Etapas de entrenamiento | 1 | 2 o más |
| Especialización | Directa | Progresiva |
| Riesgo de *forgetting* | Mayor | Menor |
| Complejidad | Media | Alta |
| Control experimental | Medio | Alto |

---

## 🚀 Lanzar la API (FastAPI)

Desde la carpeta `implementation/`:

```bash
conda activate transformers_env
uvicorn main:app --reload
```

## 🔌 Acceso a la API

| Recurso | URL |
|----------|------|
| API Base | http://localhost:8000 |
| Documentación interactiva (Swagger) | http://localhost:8000/docs |

---

## 🧪 Cómo probar el modelo

Puedes probar los modelos directamente desde la documentación interactiva (Swagger).

1. Accede a:  
   http://localhost:8000/docs  

2. Abre el endpoint:  
   `POST /predict`

3. Haz clic en **"Try it out"**

4. Ingresa uno de los siguientes ejemplos:

### 🔹 Modelo Base

```json
{
  "text": "La cena estuvo bacán",
  "model": "base"
}


{
  "text": "La cena estuvo bacán",
  "model": "sequential"
}

{
  "text": "La cena estuvo bacán",
  "model": "full"
}
```

---

## 🖥️ Lanzar el Frontend (Streamlit)

En una terminal separada:


```bash
conda activate streamlit_env
streamlit run streamlit_app.py

```

Disponible en: **http://localhost:8501**

---

## 🔄 Flujo Completo de Ejecución

```
1. conda activate transformers_env
2. uvicorn main:app --reload          ← Terminal 1

3. conda activate streamlit_env
4. streamlit run streamlit_app.py     ← Terminal 2

5. Abrir http://localhost:8501
6. Ingresar texto → Seleccionar modelo → Obtener predicción
```


---

## 📁 Estructura del Proyecto

```
spanish-nlp-fine-tuning/
│
├── fine_tuning/
│   ├── sequential-full-fine-tuning/   # Entrenamiento secuencial
│   └── spanish-bert-full-fine-tuning/ # Full fine-tuning
│
├── implementation/
│   ├── main.py                        # Backend FastAPI
│   └── streamlit_app.py               # Frontend Streamlit
│
└── README.md
```

---

## ✅ Buenas Prácticas

- No subir modelos pesados a GitHub — usar `.gitignore` o Git LFS
- Fijar semillas aleatorias para reproducibilidad (`seed=42`)
- Versionar experimentos con nombres descriptivos
- Separar claramente entrenamiento de inferencia
- Documentar hiperparámetros y métricas por experimento

---

## 🔬 Mejoras Futuras

- [ ] Early stopping con monitoreo de validación
- [ ] Cross-validation k-fold
- [ ] Métricas adicionales: F1, Recall, AUC-ROC
- [ ] Dockerización del stack completo
- [ ] Deploy en la nube (Hugging Face Spaces, AWS, GCP)
- [ ] Monitoreo de inferencia en producción (e.g., Prometheus + Grafana)

---

## 🧠 Conclusión

Este proyecto demuestra un dominio end-to-end del ciclo de vida de un modelo NLP: desde la elección del modelo base y las estrategias de fine-tuning, hasta el despliegue con una arquitectura API + frontend. La separación en entornos, la comparación empírica entre estrategias de entrenamiento y la estructura modular del código reflejan buenas prácticas de ingeniería de ML aplicada.
