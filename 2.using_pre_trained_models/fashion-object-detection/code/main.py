from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from transformers import AutoImageProcessor, AutoModelForObjectDetection
from PIL import Image
import torch
import io

# =====================================
# Inicializar FastAPI
# =====================================
app = FastAPI(
    title="Fashion Object Detection API",
    description="API para detección de objetos de moda usando Hugging Face",
    version="1.0"
)

# =====================================
# Cargar modelo (UNA SOLA VEZ)
# =====================================
MODEL_NAME = "yainage90/fashion-object-detection"

processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
model = AutoModelForObjectDetection.from_pretrained(MODEL_NAME)
model.eval()

# =====================================
# Endpoint principal
# =====================================
@app.post("/detect")
async def detect_objects(file: UploadFile = File(...)):
    # Leer la imagen
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Preprocesar
    inputs = processor(images=image, return_tensors="pt")

    # Inferencia
    with torch.no_grad():
        outputs = model(**inputs)

    # Post-procesado
    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_object_detection(
        outputs,
        threshold=0.5,
        target_sizes=target_sizes
    )[0]

    detections = []

    for score, label, box in zip(
        results["scores"],
        results["labels"],
        results["boxes"]
    ):
        detections.append({
            "label": model.config.id2label[label.item()],
            "score": round(score.item(), 3),
            "box": [round(v, 2) for v in box.tolist()]  # xmin, ymin, xmax, ymax
        })

    return JSONResponse(content={
        "image_name": file.filename,
        "num_detections": len(detections),
        "detections": detections
    })

# =====================================
# Endpoint de prueba
# =====================================
@app.get("/")
def read_root():
    return {"status": "API funcionando correctamente 🚀"}
