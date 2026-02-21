import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(page_title="NLP Sentiment Analyzer", layout="centered")

st.title("🧠 Spanish NLP Sentiment Analyzer")

st.write("Escribe un texto y selecciona el modelo que quieres usar.")

# -------- Input --------
text_input = st.text_area("Texto:", height=150)

st.subheader("Selecciona modelo(s)")

use_base = st.checkbox("Modelo Base")
use_sequential = st.checkbox("Modelo Sequential")
use_full = st.checkbox("Modelo Full Fine-Tuning")

# -------- Function --------
def get_prediction(text, model_name):
    try:
        response = requests.post(
            API_URL,
            json={"text": text, "model": model_name},
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# -------- Button --------
if st.button("Analizar"):

    if not text_input.strip():
        st.warning("Por favor ingresa un texto.")
    else:

        selected_models = []

        if use_base:
            selected_models.append("base")
        if use_sequential:
            selected_models.append("sequential")
        if use_full:
            selected_models.append("full")

        if not selected_models:
            st.warning("Selecciona al menos un modelo.")
        else:
            st.divider()

            for model in selected_models:

                st.subheader(f"Modelo: {model}")

                result = get_prediction(text_input, model)

                if "error" in result:
                    st.error(result["error"])
                else:
                    prediction = result["prediction"]
                    confidence = result["confidence"]

                    if prediction == "POS":
                        st.success(f"Predicción: {prediction}")
                    elif prediction == "NEG":
                        st.error(f"Predicción: {prediction}")
                    else:
                        st.info(f"Predicción: {prediction}")

                    st.write(f"Confianza: {confidence:.4f}")

                st.divider()
