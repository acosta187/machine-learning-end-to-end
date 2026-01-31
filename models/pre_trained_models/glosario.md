# Glosario: Framework, Servidor ASGI y Uvicorn

## ¿Qué es un Framework?

Un **framework** es un conjunto integrado de herramientas, bibliotecas y convenciones que proporciona una estructura base para desarrollar aplicaciones de software de manera más rápida, ordenada y eficiente.

### Características principales

En lugar de programar desde cero componentes comunes, el framework proporciona:

- Sistema de enrutamiento (routing)
- Conexión y gestión de bases de datos
- Mecanismos de seguridad integrados
- Manejo de formularios y validación
- Estructura organizacional del proyecto
- Plantillas y componentes reutilizables

### Analogía práctica

Un framework es comparable a una casa con cimientos, estructura y sistemas básicos ya construidos. Como desarrollador, te enfocas en personalizar y decorar los espacios, no en construir las paredes desde cero.

**Sin framework**: Construyes cada componente manualmente, desde la base.  
**Con framework**: Te concentras en la lógica de negocio y funcionalidades específicas.

### Framework vs Librería

La diferencia fundamental radica en el **principio de Inversión de Control**:

- **Librería**: Tú decides cuándo y cómo invocarla. Tienes el control del flujo.
- **Framework**: Define la estructura y flujo de la aplicación. Tú implementas dentro de sus reglas.

### Ejemplos comunes

**Frameworks web en Python**:
- **Django**: Framework completo con "baterías incluidas" (ORM, admin, autenticación, etc.)
- **FastAPI**: Moderno, orientado a APIs, con soporte asíncrono nativo
- **Flask**: Minimalista y flexible, ideal para proyectos pequeños o personalizados

**Otros lenguajes**:
- **Java**: Spring Framework
- **JavaScript**: Next.js, Angular, Vue.js
- **PHP**: Laravel, Symfony
- **Ruby**: Ruby on Rails

### Ventajas de usar un framework

- ✅ Desarrollo más rápido
- ✅ Código estandarizado y mantenible
- ✅ Reducción de errores comunes
- ✅ Facilita el trabajo en equipo
- ✅ Comunidad y documentación establecidas
- ✅ Mejores prácticas incorporadas

---

## ¿Qué es un Servidor ASGI?

**ASGI** (Asynchronous Server Gateway Interface) es una especificación que define cómo los servidores web deben comunicarse con aplicaciones Python asíncronas.

### Propósito

ASGI permite ejecutar aplicaciones web modernas que requieren:

- **WebSockets**: Comunicación bidireccional en tiempo real
- **Async/Await**: Programación asíncrona nativa de Python
- **Conexiones persistentes**: Chats, notificaciones push, streaming de datos
- **Server-Sent Events (SSE)**: Transmisión unidireccional del servidor al cliente

### ASGI como evolución de WSGI

ASGI es la evolución moderna de **WSGI** (Web Server Gateway Interface):

- **WSGI**: Estándar para aplicaciones síncronas tradicionales (HTTP request/response)
- **ASGI**: Soporta tanto operaciones síncronas como asíncronas, además de protocolos adicionales

### Frameworks compatibles con ASGI

- **FastAPI**: Diseñado nativamente para ASGI
- **Django** (3.0+): Soporte dual WSGI/ASGI
- **Starlette**: Framework asíncrono ligero
- **Quart**: Alternativa asíncrona a Flask
- **Sanic**: Framework asíncrono de alto rendimiento

### Servidores ASGI populares

Los servidores ASGI son programas que implementan la especificación ASGI y permiten que tu computadora funcione como servidor web:

1. **Uvicorn** ⭐: El más popular, rápido y fácil de usar
2. **Daphne**: Servidor oficial de Django Channels
3. **Hypercorn**: Soporta HTTP/2 y HTTP/3

### Ejemplo de uso con Uvicorn

```bash
uvicorn main:app --reload
```

Donde:
- `main`: nombre del archivo Python (main.py)
- `app`: nombre de la instancia de la aplicación
- `--reload`: reinicia automáticamente al detectar cambios (útil en desarrollo)

### Cuándo necesitas ASGI

ASGI es necesario cuando tu aplicación requiere:

- WebSockets para comunicación en tiempo real
- APIs de alto rendimiento con concurrencia
- Operaciones I/O no bloqueantes
- Streaming de datos
- Integración con librerías asíncronas modernas

### Django: WSGI vs ASGI

Django soporta ambos modos desde la versión 3.0:

- **WSGI** (`wsgi.py`): Para aplicaciones tradicionales con HTTP sincrónico
- **ASGI** (`asgi.py`): Para WebSockets, async views y operaciones asíncronas

---

## ¿Qué es Uvicorn?

**Uvicorn** es un programa que hace que tu computadora funcione como un servidor web, implementando la especificación ASGI para aplicaciones Python asíncronas.

### Función principal

Uvicorn **convierte tu PC en un servidor web** capaz de:

1. **Escuchar** conexiones entrantes en un puerto específico
2. **Recibir** peticiones HTTP/WebSocket de clientes remotos
3. **Entregar** estas peticiones a tu aplicación (FastAPI, Django, etc.)
4. **Devolver** las respuestas de tu aplicación a los clientes

### Más que un simple ejecutor

Uvicorn no solo "ejecuta funciones" Python. Es un **programa servidor completo** que:

- Gestiona el ciclo de vida de múltiples conexiones simultáneas
- Parsea y valida peticiones HTTP según los estándares web
- Maneja la concurrencia mediante el modelo async/await de Python
- Implementa el protocolo ASGI para comunicarse con tu aplicación
- Administra recursos del sistema (memoria, sockets, procesos)
- Proporciona logging y monitoreo de peticiones

En otras palabras: **transforma tu computadora en un punto de acceso web**, permitiendo que cualquier aplicación compatible con ASGI se convierta en un servicio accesible por red.

### Características técnicas

- Implementación basada en **uvloop** (loop asíncrono de alto rendimiento)
- Utiliza **httptools** para parseo rápido de HTTP
- Soporte completo de la especificación ASGI 3.0
- Compatible con HTTP/1.1 y WebSockets
- Recarga automática en modo desarrollo (hot reload)
- Logging integrado y configurable
- Bajo consumo de recursos comparado con servidores tradicionales

### Uso básico

```bash
# Servidor básico
uvicorn main:app

# Con recarga automática (desarrollo)
uvicorn main:app --reload

# Especificando host y puerto
uvicorn main:app --host 0.0.0.0 --port 8000

# Con múltiples workers (producción)
uvicorn main:app --workers 4

# Con logging personalizado
uvicorn main:app --log-level debug
```

### Parámetros comunes

- `--host`: Dirección IP donde escuchar (0.0.0.0 para todas las interfaces)
- `--port`: Puerto de escucha (por defecto 8000)
- `--reload`: Reinicia al detectar cambios en el código
- `--workers`: Número de procesos worker (para producción)
- `--log-level`: Nivel de detalle del logging (debug, info, warning, error)

### Alternativas a Uvicorn

- **Gunicorn + Uvicorn workers**: Combinación común en producción
- **Hypercorn**: Soporta HTTP/2 y HTTP/3
- **Daphne**: Oficial de Django Channels

### Cuándo usar Uvicorn

Uvicorn es ideal para:

- Desarrollo local de aplicaciones FastAPI/Starlette
- Aplicaciones Django con soporte asíncrono
- APIs REST modernas de alto rendimiento
- Aplicaciones con WebSockets
- Microservicios Python
- Prototipos rápidos que necesitan servidor web

---

## Relación entre Framework, ASGI y Uvicorn

### Flujo de una petición web

```
[Cliente] → [Uvicorn] → [Especificación ASGI] → [Framework] → [Tu código]
            (programa    (protocolo de          (FastAPI/    (lógica de
             servidor)    comunicación)          Django)      negocio)
```

### Explicación del flujo

1. El **cliente** (navegador, app móvil, etc.) hace una petición HTTP
2. **Uvicorn** (programa servidor) recibe la conexión en tu computadora y parsea la petición
3. La **especificación ASGI** define cómo Uvicorn debe entregar esa petición
4. El **framework** (FastAPI/Django) recibe la petición y la enruta según tus definiciones
5. **Tu código** procesa la lógica de negocio y genera una respuesta
6. La respuesta viaja en sentido inverso hasta el cliente

### Separación de responsabilidades

Esta arquitectura permite claridad y modularidad:

- **Uvicorn**: Maneja el protocolo de red y convierte tu PC en servidor
- **ASGI**: Define el estándar de comunicación entre servidor y aplicación
- **Framework**: Gestiona rutas, middlewares y estructura de la aplicación
- **Tu código**: Implementa la funcionalidad específica del negocio

### Ejemplo práctico completo

```python
# main.py
from fastapi import FastAPI

app = FastAPI()  # Framework

@app.get("/")
async def root():
    return {"mensaje": "Hola mundo"}  # Tu código
```

```bash
# Ejecutar el servidor
uvicorn main:app --reload
```

Cuando ejecutas este comando:
1. **Uvicorn** convierte tu computadora en un servidor web
2. Escucha en `http://localhost:8000`
3. Implementa **ASGI** para comunicarse con FastAPI
4. **FastAPI** (framework) maneja el enrutamiento
5. Tu función `root()` procesa la petición y devuelve la respuesta

---

## Resumen conceptual

| Concepto | ¿Qué es? | Ejemplo |
|----------|----------|---------|
| **Framework** | Estructura y herramientas para desarrollar aplicaciones | Django, FastAPI, Flask |
| **ASGI** | Especificación/protocolo de comunicación asíncrona | Estándar que define cómo conectar servidor y app |
| **Uvicorn** | Programa que convierte tu PC en servidor web ASGI | Software que ejecutas para servir tu aplicación |

**Analogía final**: Si tu aplicación web fuera un restaurante:
- **Framework**: La cocina equipada con todos los utensilios
- **ASGI**: El protocolo de comunicación entre meseros y cocina
- **Uvicorn**: El edificio que convierte el espacio en un restaurante funcional y accesible al público
