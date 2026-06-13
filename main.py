from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from database import Base, engine, get_db
import models

from sqlalchemy.orm import Session

from google import genai
from dotenv import load_dotenv

app = FastAPI()
Base.metadata.create_all(bind=engine)
load_dotenv()
gemini_client = genai.Client()

@app.get("/")
def root():
    return {"mensaje": "Hola desde FastAPI"}

class Activo(BaseModel):
    ticker: str = Field(max_length=5)
    nombre: str
    precio: float = Field(gt=0)  # greater than 0
    cantidad: float = Field(default=0.0, ge=0)  # greater or equal 0

class Pregunta(BaseModel):
    texto: str

class PreguntaActivo(BaseModel):
    ticker: str
    pregunta: str


@app.get("/activos")
def listar_activos(db: Session = Depends(get_db)):
    return db.query(models.Activo).all()

@app.get("/activos/{ticker}")
def obtener_activo(ticker: str, db: Session = Depends(get_db)):
    activo = db.query(models.Activo).filter(models.Activo.ticker == ticker).first()
    if activo is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    return activo

@app.get("/buscar")
def buscar_activos(ticker: str = None, min_precio: float = None):
    return {"ticker": ticker, "min_precio": min_precio}

@app.post("/activos")
def crear_activo(activo: Activo, db: Session = Depends(get_db)):
    nuevo_activo = models.Activo(**activo.model_dump())
    db.add(nuevo_activo)
    db.commit()
    db.refresh(nuevo_activo)
    return nuevo_activo

@app.post("/preguntar")
def preguntar_ia(pregunta: Pregunta):
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=pregunta.texto
    )
    return {"respuesta": response.text}

@app.post("/preguntar-activo")
def preguntar_sobre_activo(data: PreguntaActivo, db: Session = Depends(get_db)):
    activo = db.query(models.Activo).filter(models.Activo.ticker == data.ticker).first()
    if activo is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    
    contexto = f"""
    Tengo el siguiente activo en mi cartera:
    - Ticker: {activo.ticker}
    - Nombre: {activo.nombre}
    - Precio actual: {activo.precio}
    - Cantidad: {activo.cantidad}
    
    Pregunta del usuario: {data.pregunta}
    
    Responde de forma concisa y útil para un inversor.
    """
    
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contexto
    )
    return {"respuesta": response.text}

@app.put("/activos/{ticker}")
def actualizar_activo(ticker: str, activo_nuevo: Activo, db: Session = Depends(get_db)):
    activo = db.query(models.Activo).filter(models.Activo.ticker == ticker).first()
    if activo is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    
    activo.ticker = activo_nuevo.ticker
    activo.nombre = activo_nuevo.nombre
    activo.precio = activo_nuevo.precio
    activo.cantidad = activo_nuevo.cantidad

    # for key, value in activo_nuevo.model_dump().items():   -----> Esto es mas profesional
    #     setattr(activo, key, value)
    
    db.commit()
    db.refresh(activo)
    return activo

@app.delete("/activos/{ticker}")
def eliminar_activo(ticker: str, db: Session = Depends(get_db)):
    activo = db.query(models.Activo).filter(models.Activo.ticker == ticker).first()
    if activo is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    db.delete(activo)
    db.commit()
    return {"detalle": f"{ticker} borrado exitosamente"}