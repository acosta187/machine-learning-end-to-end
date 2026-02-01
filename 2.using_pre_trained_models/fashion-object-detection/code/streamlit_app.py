import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
import io

# ===============================
# Configuración
# ===============================
API_URL = "http://127.0.0.1:8000/detect"

st.set_page_config(
    page_title="YOLO Object Detection",
    layout="centered"
)

st.title("🔍 Detección de Objetos con YOLO")
st.write("Sube una imagen y se mostrarán los objetos detectados")

# ===============================
# Upload de imagen
# ===============================
uploaded_file = st.file_uploader(
    "Sube una imagen",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    # Mostrar imagen original
    image = Image.open(uploaded_file).convert("RGB")
    st.subheader("📷 Imagen original")
    st.image(image, use_container_width=True)

    if st.button("Detectar objetos 🚀"):
        with st.spinner("Enviando imagen al modelo..."):
            # Enviar imagen al API
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }

            response = requests.post(API_URL, files=files)

        if response.status_code != 200:
            st.error("Error al procesar la imagen en el API")
        else:
            data = response.json()
            detections = data.get("detections", [])

            # ===============================
            # Dibujar bounding boxes
            # ===============================
            draw = ImageDraw.Draw(image)

            try:
                font = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
            except:
                font = ImageFont.load_default()

            for det in detections:
                xmin, ymin, xmax, ymax = det["box"]
                label = det["label"]
                score = det["score"]

                # Caja
                draw.rectangle(
                    [(xmin, ymin), (xmax, ymax)],
                    outline="red",
                    width=3
                )

                # Texto
                text = f"{label} ({score:.2f})"
                text_size = draw.textbbox((0, 0), text, font=font)

                draw.rectangle(
                    [
                        xmin,
                        ymin - (text_size[3] - text_size[1]) - 4,
                        xmin + (text_size[2] - text_size[0]) + 4,
                        ymin
                    ],
                    fill="red"
                )

                draw.text(
                    (xmin + 2, ymin - (text_size[3] - text_size[1]) - 2),
                    text,
                    fill="white",
                    font=font
                )

            # ===============================
            # Mostrar resultado
            # ===============================
            st.subheader("📦 Objetos detectados")
            st.image(image, use_container_width=True)

            st.success(f"Detecciones: {len(detections)}")

            if detections:
                st.json(detections)
