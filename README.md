# FastAPI Learning

Proyecto de aprendizaje de FastAPI — API REST con CRUD completo, persistencia con SQLAlchemy, validaciones con Pydantic y manejo de errores.

## Stack
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Uvicorn

## Ejecutar
```bash
uvicorn main:app --reload
```

## Endpoints
- GET /activos
- GET /activos/{ticker}
- POST /activos
- PUT /activos/{ticker}
- DELETE /activos/{ticker}

## Conceptos aplicados
- Modelos de base de datos con SQLAlchemy (`models.py`)
- Inyección de dependencias con `Depends` para gestión de sesiones de base de datos
- Validación de datos con Pydantic (`Field`, tipos, valores por defecto)
- Manejo de errores con `HTTPException`