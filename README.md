# FastAPI Learning

Proyecto de aprendizaje de FastAPI — API REST con CRUD completo, autenticación JWT, integración con Yahoo Finance, RAG con Google Gemini y persistencia con PostgreSQL.

## Stack

- FastAPI
- SQLAlchemy
- PostgreSQL (Docker)
- Pydantic
- Uvicorn
- python-jose (JWT)
- Google Gemini (RAG)

## Requisitos

- Python 3.11+
- Docker

## Puesta en marcha

1. Instalar dependencias:
```bash
   pip install -r requirements.txt
```

2. Copiar la plantilla de variables de entorno:
```bash
   cp .env.example .env
```
   Rellenar las variables (credenciales de BBDD, `GEMINI_API_KEY`, `SECRET_KEY`).

3. Levantar PostgreSQL:
```bash
   docker compose up -d
```

4. Arrancar la API:
```bash
   uvicorn main:app --reload
```

La API estará en `http://localhost:8000`. Documentación interactiva en `/docs`.

## Endpoints principales

- Autenticación: `POST /registro`, `POST /login`
- Activos: `GET/POST/PUT/DELETE /activos`
- Compras: `GET/POST /compras`
- IA: `POST /preguntar-activo`

## Conceptos aplicados

- Modelos de base de datos con SQLAlchemy
- Inyección de dependencias con `Depends`
- Validación con Pydantic
- JWT con python-jose + argon2
- BackgroundTasks para logs asíncronos
- RAG con Google Gemini
- Tests con pytest y BBDD separada
- CI/CD con GitHub Actions