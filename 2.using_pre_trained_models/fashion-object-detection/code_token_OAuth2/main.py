from fastapi import FastAPI, File, UploadFile, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from transformers import AutoImageProcessor, AutoModelForObjectDetection
from PIL import Image
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import torch
import io

# =====================================
# Configuración JWT
# =====================================
SECRET_KEY = "clave_super_secreta_cambiame_en_produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30# mofificar el tiempo de expiración del token

# =====================================
# Usuario hardcodeado para demo
# =====================================
# Usamos sha256_crypt para evitar bug de compatibilidad entre passlib y bcrypt>=4.x
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

FAKE_USERS = {
    "admin": {
        "username": "admin",
        # Hash de "1234"
        "hashed_password": pwd_context.hash("1234"),
    }
}

# =====================================
# OAuth2
# =====================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# =====================================
# Inicializar FastAPI
# =====================================
app = FastAPI(
    title="Fashion Object Detection API",
    description="API para detección de objetos de moda usando Hugging Face",
    version="2.0"
)

# =====================================
# Cargar modelo (UNA SOLA VEZ)
# =====================================
MODEL_NAME = "yainage90/fashion-object-detection"

processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
model = AutoModelForObjectDetection.from_pretrained(MODEL_NAME)
model.eval()

# =====================================
# Funciones JWT
# =====================================
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = FAKE_USERS.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username not in FAKE_USERS:
            raise HTTPException(status_code=401, detail="Token inválido")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

# =====================================
# Endpoint de login
# =====================================
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# =====================================
# Endpoint principal (protegido con JWT)
# =====================================
@app.post("/detect")
async def detect_objects(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)   # <-- reemplaza el token manual
):
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

# =====================================
# Correr con: uvicorn main:app --reload
# =====================================
