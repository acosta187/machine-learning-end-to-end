


```bash
conda activate transformers_env
uvicorn main:app --reload
```

```bash
conda activate data_science
streamlit run streamlit_app.py
```


# Ejecución de una API con FastAPI usando Uvicorn

Este proyecto utiliza **FastAPI** como framework para crear una API REST y **Uvicorn** como servidor ASGI para ejecutarla.

---

## ¿Por qué es necesario Uvicorn?

FastAPI **no es un servidor web**.  
FastAPI solo define:
- Rutas (`endpoints`)
- Lógica de negocio
- Validación de datos

Para que la API pueda:
- Escuchar peticiones HTTP
- Mantener conexiones activas
- Responder a clientes (navegador, Python, curl, etc.)

se necesita un **servidor ASGI**, y el más usado es **Uvicorn**.

---

## Forma estándar de lanzar una API con FastAPI

La forma más común, recomendada y estándar de ejecutar una aplicación FastAPI es:

```bash
uvicorn main:app --reload
```

Esta es la forma utilizada en:
- Documentación oficial de FastAPI
- Tutoriales profesionales
- Desarrollo local
- Proyectos reales

---

### Lanzar la interfaz grafica usando streamlit

```bash
streamlit run streamlit_app.py
```


![Aplicacion corriendo en streamlit que consume el API creada a aprtir del modelo yainage90/fashion-object-detection](multimedia/ex.png)

## Explicación del comando

```bash
uvicorn main:app --reload
```

### 1. `uvicorn`
Es el servidor ASGI que ejecuta la aplicación.
Se encarga de:
- Recibir solicitudes HTTP
- Enrutarlas a FastAPI
- Enviar las respuestas al cliente

### 2. `main`
Hace referencia al archivo `main.py`.

Ejemplo:
```
main.py
```

### 3. `app`
Es el objeto FastAPI definido dentro de `main.py`.

Ejemplo:
```python
from fastapi import FastAPI

app = FastAPI()
```

### 4. `main:app`
Significa:
"Usa el objeto `app` que está dentro del archivo `main.py`"

### 5. `--reload`
Activa la recarga automática.
Esto significa que:
- Cada vez que se guarda un cambio en el código
- El servidor se reinicia automáticamente

⚠️ `--reload` solo debe usarse en desarrollo, no en producción.

---

## Ejemplo completo

### Estructura del proyecto:
```
project/
├── main.py
```

### Contenido de `main.py`:
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "API funcionando"}
```

### Ejecución:
```bash
uvicorn main:app --reload
```

La API quedará disponible en:
- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs (Swagger UI)

---

## Forma estándar en producción

En producción, la forma recomendada es usar Gunicorn con workers de Uvicorn:

```bash
gunicorn main:app -k uvicorn.workers.UvicornWorker -w 4
```

Esto permite:
- Manejar múltiples usuarios
- Mejor rendimiento
- Mayor estabilidad

---

## Resumen

- FastAPI define la API
- Uvicorn ejecuta la API
- `main:app` indica dónde está la aplicación
- `--reload` facilita el desarrollo
- `uvicorn main:app --reload` es la forma estándar de ejecución

---

## Conclusión

Usar Uvicorn no es opcional: es la manera correcta y profesional de ejecutar una aplicación FastAPI, tanto en desarrollo como en producción.
