import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
import io

# ===============================
# Configuración
# ===============================
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="YOLO Object Detection",
    layout="centered"
)

# ===============================
# Funciones de autenticación
# ===============================
def login(username: str, password: str):
    """Hace request al endpoint /login y retorna el token."""
    response = requests.post(
        f"{API_URL}/login",
        data={"username": username, "password": password}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def get_auth_headers():
    """Retorna los headers con el token JWT guardado en session_state."""
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"}

# ===============================
# Inicializar session_state
# ===============================
if "token" not in st.session_state:
    st.session_state["token"] = None

# ===============================
# Formulario de login
# ===============================
if st.session_state["token"] is None:
    st.title("🔐 Iniciar sesión")
    st.write("Usuario demo: **admin** / Contraseña: **1234**")

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        token = login(username, password)
        if token:
            st.session_state["token"] = token
            st.success("✅ Login exitoso")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos")

# ===============================
# App principal (requiere login)
# ===============================
else:
    st.title("🔍 Detección de Objetos con YOLO")
    st.write("Sube una imagen y se mostrarán los objetos detectados")

    # Botón de logout
    if st.button("Cerrar sesión"):
        st.session_state["token"] = None
        st.rerun()

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
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }
                response = requests.post(
                    f"{API_URL}/detect",
                    files=files,
                    headers=get_auth_headers()
                )

            # Manejar error de autenticación
            if response.status_code == 401:
                st.error("⚠️ Sesión expirada. Por favor vuelve a iniciar sesión.")
                st.session_state["token"] = None
                st.rerun()
            elif response.status_code != 200:
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

# ===============================
# Correr con: streamlit run streamlit_app.py
# ===============================
