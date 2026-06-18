from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
import sys
sys.path.insert(0, '..')
import models
from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from decimal import Decimal


load_dotenv()
gemini_client = genai.Client()

router = APIRouter()

class Activo(BaseModel):
    ticker: str = Field(max_length=5)
    nombre: str

class ActivoResponse(BaseModel):
    id: int
    ticker: str
    nombre: str
    precio: Decimal | None = None
    cantidad: Decimal | None = None
    
    class Config:
        from_attributes = True

class Pregunta(BaseModel):
    texto: str

class PreguntaActivo(BaseModel):
    ticker: str
    pregunta: str


@router.get("/activos", response_model=list[ActivoResponse])
def listar_activos(db: Session = Depends(get_db)):
    activos = db.query(models.Activo).all()
    resultado = []
    for activo in activos:
        compras = db.query(models.Compra).filter(models.Compra.activo_id == activo.id).all()
        cantidad = sum(c.cantidad for c in compras) if compras else 0
        resultado.append(ActivoResponse(
            id=activo.id,
            ticker=activo.ticker,
            nombre=activo.nombre,
            cantidad=cantidad,
            precio=None
        ))
    return resultado

# from sqlalchemy import func

# @router.get("/activos", response_model=list[ActivoResponse])
# def listar_activos(db: Session = Depends(get_db)):
#     activos = db.query(models.Activo).all()
#     resultado = []
#     for activo in activos:
#         cantidad = db.query(func.sum(models.Compra.cantidad))\
#             .filter(models.Compra.activo_id == activo.id)\                        PARA CALCULOS EN LA BASE DE DATOS DIRECTAMENTE SIN TRAER LOS DATOS EN LOOP AL BACKEND
#             .scalar() or 0
#         resultado.append(ActivoResponse(
#             id=activo.id,
#             ticker=activo.ticker,
#             nombre=activo.nombre,
#             cantidad=float(cantidad),
#             precio=None
#         ))
#     return resultado

@router.get("/activos/{ticker}")
def obtener_activo(ticker: str, db: Session = Depends(get_db)):
    activo = db.query(models.Activo).filter(models.Activo.ticker == ticker).first()
    if activo is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    return activo


@router.post("/activos")
def crear_activo(activo: Activo, db: Session = Depends(get_db)):
    nuevo_activo = models.Activo(**activo.model_dump())
    db.add(nuevo_activo)
    db.commit()
    db.refresh(nuevo_activo)
    return nuevo_activo

@router.post("/preguntar")
def preguntar_ia(pregunta: Pregunta):
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=pregunta.texto
    )
    return {"respuesta": response.text}

@router.post("/preguntar-activo")
def preguntar_sobre_activo(data: PreguntaActivo, db: Session = Depends(get_db)):
    activo = db.query(models.Activo).filter(models.Activo.ticker == data.ticker).first()
    if activo is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    
    compras = db.query(models.Compra).filter(models.Compra.activo_id == activo.id).all()
    
    compras_texto = "\n".join([
        f"  - {c.cantidad} acciones a {c.precio}$ el {c.fecha_compra}"
        for c in compras
    ])
    
    contexto = f"""
    Tengo el siguiente activo en mi cartera:
    - Ticker: {activo.ticker}
    - Nombre: {activo.nombre}
    - Precio actual: {activo.precio}$
    - Cantidad total: {activo.cantidad}
    
    Historial de compras:
    {compras_texto if compras_texto else "Sin compras registradas"}
    
    Pregunta: {data.pregunta}
    
    Responde de forma concisa y útil para un inversor.
    """
    
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contexto
    )
    return {"respuesta": response.text}

@router.put("/activos/{ticker}")
def actualizar_activo(ticker: str, activo_nuevo: Activo, db: Session = Depends(get_db)):
    activo = db.query(models.Activo).filter(models.Activo.ticker == ticker).first()
    if activo is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    
    activo.ticker = activo_nuevo.ticker
    activo.nombre = activo_nuevo.nombre

    # for key, value in activo_nuevo.model_dump().items():   -----> Esto es mas profesional
    #     setattr(activo, key, value)
    
    db.commit()
    db.refresh(activo)
    return activo

@router.delete("/activos/{ticker}")
def eliminar_activo(ticker: str, db: Session = Depends(get_db)):
    activo = db.query(models.Activo).filter(models.Activo.ticker == ticker).first()
    if activo is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    db.delete(activo)
    db.commit()
    return {"detalle": f"{ticker} borrado exitosamente"}