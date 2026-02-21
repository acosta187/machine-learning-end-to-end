
# Guía de Instalación y Entrenamiento con GPU (Quadro P2200)

Esta guía está optimizada para:
- GPU: NVIDIA Quadro P2200 (5 GB VRAM)
- Uso académico
- Modelos de NLP (BERT)
- Computer Vision (Transfer Learning)

---

## 1. Crear entorno Conda

```bash
conda create -n ia_gpu python=3.10 -y
conda activate ia_gpu
```

---

## 2. Instalar PyTorch con soporte GPU

```bash
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
```

Verificación:

```python
import torch
print("CUDA disponible:", torch.cuda.is_available())
print("GPU:", torch.cuda.get_device_name(0))
```

---

## 3. Instalar TensorFlow con GPU

```bash
pip install tensorflow==2.15
```

Verificación:

```python
import tensorflow as tf
print(tf.config.list_physical_devices('GPU'))
```

Habilitar crecimiento de memoria (recomendado):

```python
gpus = tf.config.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
```

---

## 4. Instalar Transformers y herramientas NLP

```bash
pip install transformers datasets accelerate sentencepiece
```

Opcional:

```bash
pip install pandas scikit-learn matplotlib
```

---

# Recomendaciones para Entrenamiento

## A. BERT (NLP)

### Configuración recomendada (5 GB VRAM)

| Parámetro | Valor recomendado |
|-----------|------------------|
| Batch size | 4 – 8 |
| Max length | 128 – 256 |
| Learning rate | 2e-5 |
| Epochs | 3 – 5 |
| Mixed precision | Sí (fp16) si es posible |

### Ejemplo básico (PyTorch)

```python
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
```

Para evitar errores de memoria:
- Reducir batch size
- Reducir max_length
- Usar gradient accumulation

---

## B. Computer Vision (Transfer Learning)

La Quadro P2200 funciona muy bien con modelos ligeros.

### Modelos recomendados

- MobileNetV2
- ResNet18 / ResNet34
- EfficientNet-B0

Evitar:
- ResNet50+ con batch grande
- EfficientNet grandes (B4+)

### Configuración recomendada

| Parámetro | Valor |
|-----------|------|
| Batch size | 16 – 32 |
| Input size | 224x224 |
| Learning rate | 1e-4 |
| Epochs | 10 – 30 |

### Ejemplo MobileNetV2 (TensorFlow)

```python
from tensorflow.keras.applications import MobileNetV2

base_model = MobileNetV2(
    weights="imagenet",
    include_top=False,
    input_shape=(224, 224, 3)
)

base_model.trainable = False
```

---

# Optimización de Memoria GPU

## Ver uso de GPU

```bash
nvidia-smi
```

Durante entrenamiento deberías ver:
- GPU Utilization > 30%
- Memoria cercana al límite

---

## Si aparece error: "CUDA out of memory"

Soluciones:
1. Reducir batch size
2. Reducir resolución de imagen
3. Usar modelos más pequeños
4. Activar mixed precision

---

# Buenas prácticas para proyectos académicos

### NLP
- Limitar longitud de texto
- Usar modelos base (bert-base)
- Guardar checkpoints

### Computer Vision
- Usar Transfer Learning
- Congelar capas iniciales
- Aumentar datos (Data Augmentation)

---

# Resumen para Quadro P2200 (5 GB)

| Tipo | Batch recomendado |
|------|------------------|
| BERT | 4 – 8 |
| MobileNetV2 | 16 – 32 |
| ResNet18 | 16 |
| ResNet50 | 4 – 8 |

---

# Verificación final del entorno

```python
import torch
import tensorflow as tf

print("PyTorch CUDA:", torch.cuda.is_available())
print("TensorFlow GPUs:", tf.config.list_physical_devices('GPU'))
```

---

# Entorno recomendado

- Python 3.10
- PyTorch + CUDA 11.8
- TensorFlow 2.15
- Transformers
- GPU activa

Este entorno es adecuado para:
- Proyectos de curso
- Transfer Learning
- NLP con BERT
- Computer Vision con modelos ligeros
