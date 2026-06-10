from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

@app.get("/")
def root():
    return {"mensaje": "Hola desde FastAPI"}

class Activo(BaseModel):
    ticker: str = Field(max_length=5)
    nombre: str
    precio: float = Field(gt=0)  # greater than 0
    cantidad: float = Field(default=0.0, ge=0)  # greater or equal 0

activos_db = []  # lista en memoria por ahora

@app.get("/activos")
def listar_activos():
    return activos_db

@app.get("/activos/{ticker}")
def obtener_activo(ticker: str):
    return {"ticker": ticker, "mensaje": f"Datos de {ticker}"}

@app.get("/buscar")
def buscar_activos(ticker: str = None, min_precio: float = None):
    return {"ticker": ticker, "min_precio": min_precio}

@app.post("/activos")
def crear_activo(activo: Activo):
    activos_db.append(activo)
    return activo

@app.put("/activos/{ticker}")
def actualizar_activo(ticker: str, activo_nuevo: Activo):
    for i, a in enumerate(activos_db):
        if a.ticker == ticker:
            activos_db[i] = activo_nuevo
            return activo_nuevo
    raise HTTPException(status_code=404, detail="Activo no encontrado")

@app.delete("/activos/{ticker}")
def eliminar_activo(ticker: str):
    global activos_db
    if not any(a.ticker == ticker for a in activos_db):
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    activos_db = [a for a in activos_db if a.ticker != ticker]
    return f'{ticker} borrado exitosamente'