# Documentacion: API de Deteccion de Objetos con Autenticacion OAuth2 y JWT

## Indice

1. Conceptos fundamentales
2. Arquitectura del sistema
3. Flujo de autenticacion
4. Como ejecutar el proyecto
5. Como usar el aplicativo
6. Consideraciones de seguridad
7. Dependencias requeridas

---

## 1. Conceptos fundamentales

### Que es OAuth2

OAuth2 es un protocolo de autorizacion estandar que define como una aplicacion puede obtener acceso limitado a recursos en nombre de un usuario. En este proyecto se utiliza el flujo denominado **Password Flow** (tambien conocido como Resource Owner Password Credentials), que es el mas directo: el usuario proporciona su nombre de usuario y contrasena directamente a la aplicacion, y esta los intercambia por un token de acceso.

Este flujo es apropiado para aplicaciones de confianza donde el cliente y el servidor pertenecen al mismo sistema, como es el caso de este proyecto con FastAPI y Streamlit.

### Que es JWT

JWT (JSON Web Token) es un estandar abierto (RFC 7519) para transmitir informacion de forma segura entre partes como un objeto JSON. Un token JWT esta compuesto por tres partes separadas por puntos:

```
header.payload.signature
```

- **Header**: contiene el tipo de token y el algoritmo de firma (en este caso, HS256).
- **Payload**: contiene los datos o "claims", como el nombre de usuario y la fecha de expiracion.
- **Signature**: es la firma digital generada con una clave secreta que garantiza que el token no fue alterado.

Un ejemplo de token JWT decodificado en su parte de payload:

```json
{
  "sub": "admin",
  "exp": 1718000000
}
```

El campo `sub` (subject) identifica al usuario. El campo `exp` indica el momento exacto en que el token deja de ser valido, expresado en tiempo Unix.

### Por que JWT y no un token estatico

En el codigo original, la autenticacion se realizaba con un token fijo hardcodeado (`mi_token_secreto_123`). Esto tiene varios problemas:

- El token nunca expira, por lo que si es interceptado, puede usarse indefinidamente.
- No hay forma de asociar el token a un usuario especifico.
- No existe un mecanismo de login real.

Con JWT, cada sesion genera un token unico con expiracion definida. El servidor puede verificar la identidad del usuario y la validez del token sin necesidad de consultar una base de datos en cada solicitud, ya que toda la informacion necesaria esta dentro del token y protegida por la firma.

### Que es bcrypt y sha256_crypt

Las contrasenas nunca deben almacenarse en texto plano. En su lugar se almacena un hash, que es el resultado de aplicar una funcion matematica unidireccional a la contrasena. Cuando el usuario ingresa su contrasena, se vuelve a aplicar la funcion y se compara el resultado con el hash almacenado.

En este proyecto se usa `sha256_crypt` a traves de la libreria `passlib`. Se eligio esta variante en lugar de `bcrypt` por razones de compatibilidad con versiones modernas de la libreria `bcrypt` (a partir de la version 4.x), que genera errores al ser usada con `passlib` en ciertos entornos.

---

## 2. Arquitectura del sistema

El sistema esta compuesto por dos procesos independientes que se comunican via HTTP:

```
[Usuario]
    |
    v
[Streamlit - Frontend]  <-->  [FastAPI - Backend]
    puerto 8501                   puerto 8000
```

El backend expone tres endpoints:

| Endpoint | Metodo | Descripcion | Protegido |
|----------|--------|-------------|-----------|
| `/`      | GET    | Verificacion de estado de la API | No |
| `/login` | POST   | Recibe credenciales y devuelve un JWT | No |
| `/detect`| POST   | Recibe una imagen y devuelve detecciones | Si (JWT) |

---

## 3. Flujo de autenticacion

El proceso completo de autenticacion funciona de la siguiente manera:

**Paso 1 - Login**

El usuario ingresa su nombre de usuario y contrasena en el formulario de Streamlit. El frontend envia una solicitud POST al endpoint `/login` con estos datos en formato de formulario (`application/x-www-form-urlencoded`), que es el formato que exige el estandar OAuth2 Password Flow.

**Paso 2 - Validacion y generacion del token**

El backend recibe las credenciales, verifica que el usuario exista y que la contrasena coincida con el hash almacenado. Si la validacion es correcta, genera un JWT firmado con la clave secreta y lo devuelve al cliente en la siguiente estructura:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Paso 3 - Almacenamiento del token**

Streamlit guarda el token en `st.session_state`, que es el mecanismo de Streamlit para mantener estado entre interacciones del usuario dentro de la misma sesion del navegador. El token no se almacena en disco ni en el navegador de forma persistente.

**Paso 4 - Uso del token en solicitudes protegidas**

Cada vez que el usuario solicita una deteccion de objetos, Streamlit incluye el token en el header HTTP de la solicitud:

```
Authorization: Bearer <token>
```

**Paso 5 - Verificacion del token en el backend**

El backend, a traves del mecanismo `Depends(get_current_user)` de FastAPI, intercepta la solicitud antes de procesarla, extrae el token del header, verifica su firma y comprueba que no haya expirado. Si el token es valido, la solicitud continua. Si no, devuelve un error 401.

**Paso 6 - Expiracion**

El token tiene una validez de 30 minutos desde el momento en que fue generado. Cuando expira, el backend devuelve un 401. Streamlit detecta este codigo de error, elimina el token del estado de sesion y redirige al usuario al formulario de login.

---

## 4. Como ejecutar el proyecto

### Requisitos previos

Tener instalado Python 3.9 o superior y un entorno virtual activo (recomendado).

### Instalacion de dependencias

```bash
pip install fastapi uvicorn python-jose[cryptography] passlib streamlit requests transformers pillow torch
```

### Ejecutar el backend

Desde el directorio donde se encuentra `main.py`:

```bash
uvicorn main:app --reload
```

El servidor quedara disponible en `http://127.0.0.1:8000`. La opcion `--reload` hace que el servidor se reinicie automaticamente ante cambios en el codigo.

### Ejecutar el frontend

En una terminal separada, desde el directorio donde se encuentra `streamlit_app.py`:

```bash
streamlit run streamlit_app.py
```

La aplicacion quedara disponible en `http://localhost:8501`.

El orden importa: el backend debe estar corriendo antes de iniciar el frontend.

---

## 5. Como usar el aplicativo

### Inicio de sesion

Al ingresar a `http://localhost:8501`, el sistema mostrara un formulario de login. Ingresar las siguientes credenciales de demo:

- Usuario: `admin`
- Contrasena: `1234`

Presionar el boton "Iniciar sesion". Si las credenciales son correctas, la aplicacion cargara automaticamente la pantalla principal.

### Deteccion de objetos

Una vez autenticado, la interfaz muestra un campo para subir una imagen. El proceso es el siguiente:

1. Hacer clic en "Sube una imagen" y seleccionar un archivo en formato PNG, JPG o JPEG.
2. La imagen se mostrara en pantalla una vez cargada.
3. Hacer clic en "Detectar objetos".
4. El sistema enviara la imagen al backend junto con el token de autenticacion.
5. El modelo de Hugging Face (`yainage90/fashion-object-detection`) procesara la imagen.
6. Se mostrara la imagen con bounding boxes dibujados sobre los objetos detectados, junto con el nombre de la categoria y el nivel de confianza.
7. Debajo de la imagen se desplegara la respuesta en formato JSON con el detalle de cada deteccion.

### Cierre de sesion

En la parte superior de la pantalla principal hay un boton "Cerrar sesion". Al presionarlo, el token se elimina del estado de sesion y el sistema regresa al formulario de login.

### Expiracion automatica de la sesion

Si el token expira mientras se usa la aplicacion (pasados los 30 minutos), el sistema mostrara un mensaje de advertencia y redirigira automaticamente al formulario de login. No es necesario hacer ninguna accion manual: basta con volver a iniciar sesion para continuar usando el servicio.

---

## 6. Consideraciones de seguridad

### Clave secreta

La variable `SECRET_KEY` en `main.py` es la clave con la que se firman y verifican todos los tokens JWT. En el codigo de demo tiene un valor simple para facilitar las pruebas. En un entorno de produccion, esta clave debe:

- Ser larga y aleatoria (minimo 32 caracteres).
- No estar hardcodeada en el codigo fuente.
- Cargarse desde una variable de entorno o un gestor de secretos.

Ejemplo de como leerla desde una variable de entorno:

```python
import os
SECRET_KEY = os.environ.get("SECRET_KEY")
```

### Usuarios en produccion

El diccionario `FAKE_USERS` es adecuado para una demo. En un sistema real, los usuarios y sus hashes deben almacenarse en una base de datos, y las contrasenas deben ser generadas con un algoritmo seguro antes de su almacenamiento, nunca en texto plano.

### HTTPS

Este proyecto corre sobre HTTP local. En produccion, toda la comunicacion debe realizarse sobre HTTPS para evitar que los tokens sean interceptados durante la transmision.

### Expiracion del token

El valor de 30 minutos para la expiracion del token es un balance entre seguridad y comodidad. Puede ajustarse modificando la variable `ACCESS_TOKEN_EXPIRE_MINUTES` en `main.py`.

---

## 7. Dependencias requeridas

| Libreria | Uso |
|----------|-----|
| `fastapi` | Framework del backend |
| `uvicorn` | Servidor ASGI para correr FastAPI |
| `python-jose[cryptography]` | Generacion y verificacion de tokens JWT |
| `passlib` | Hashing y verificacion de contrasenas |
| `streamlit` | Interfaz de usuario del frontend |
| `requests` | Solicitudes HTTP desde Streamlit al backend |
| `transformers` | Carga del modelo de deteccion de Hugging Face |
| `pillow` | Procesamiento de imagenes y dibujado de bounding boxes |
| `torch` | Backend de inferencia del modelo |
