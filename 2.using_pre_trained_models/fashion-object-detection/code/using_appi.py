

import requests
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ===============================
# Configuración
# ===============================
API_URL = "http://127.0.0.1:8000/detect"
IMAGE_PATH = "/home/carlos/Downloads/foto1.jpg"


# ===============================
# Enviar imagen al API
# ===============================
with open(IMAGE_PATH, "rb") as f:
    response = requests.post(API_URL, files={"file": f})

data = response.json()
detections = data["detections"]
detections




# ===============================
# Abrir imagen original
# ===============================
image = Image.open(IMAGE_PATH).convert("RGB")

fig, ax = plt.subplots(1, figsize=(8, 8))
ax.imshow(image)

# ===============================
# Dibujar cajas
# ===============================
for det in detections:
    xmin, ymin, xmax, ymax = det["box"]
    label = det["label"]
    score = det["score"]

    width = xmax - xmin
    height = ymax - ymin

    rect = patches.Rectangle(
        (xmin, ymin),
        width,
        height,
        linewidth=2,
        edgecolor="red",
        facecolor="none"
    )

    ax.add_patch(rect)

    ax.text(
        xmin,
        ymin - 5,
        f"{label} ({score})",
        color="red",
        fontsize=10,
        bbox=dict(facecolor="white", alpha=0.7)
    )

ax.axis("off")
plt.show()
