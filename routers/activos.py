from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
import sys
sys.path.insert(0, '..')
import models
from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal
import yfinance as yf
from auth import obtener_usuario_actual


load_dotenv()
gemini_client = genai.Client()

router = APIRouter()

class Activo(BaseModel):
    ticker: str = Field(max_length=5)
    nombre: str

    @field_validator('ticker')
    @classmethod
    def ticker_formato(cls, v):
        if len(v) > 10:
            raise ValueError('Ticker demasiado largo')
        return v.upper()

class CompraEnActivo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    fecha_compra: str
    precio: float
    cantidad: float
    tipo_cambio: float

class ActivoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    ticker: str
    nombre: str
    precio: Decimal | None = None
    cantidad: Decimal | None = None
    compras: list[CompraEnActivo] = []

class Pregunta(BaseModel):
    texto: str

class PreguntaActivo(BaseModel):
    ticker: str
    pregunta: str

class CarteraResumenResponse(BaseModel):
    total_activos : int
    total_compras : int

class RendimientoResponse(BaseModel):
    ticker: str
    total_invertido: float | None = None
    valor_actual: float | None = None
    ganancia: float | None = None
    porcentaje: float | None = None

class ComparacionResponse(BaseModel):
    ticker1:str
    precio_actual1:Decimal
    total_invertido1:Decimal
    cantidad_acciones1:Decimal
    total_dividendos1:Decimal
    cantidad_dividendos1: Decimal
    ticker2:str
    precio_actual2:Decimal
    total_invertido2:Decimal
    cantidad_acciones2:Decimal
    total_dividendos2:Decimal
    cantidad_dividendos2: Decimal   


def registrar_log(ticker: str, nombre: str):
    print(f"LOG: Se ha creado el activo {ticker} - {nombre}")


@router.get("/activos", response_model=list[ActivoResponse])
def listar_activos(db: Session = Depends(get_db), usuario = Depends(obtener_usuario_actual)):
    activos = db.query(models.Activo).filter(models.Activo.usuario_id == usuario.id).all()
    resultado = []
    for activo in activos:
        compras = activo.compras
        cantidad = sum(c.cantidad for c in compras) if compras else 0
        
        ticker_yf = yf.Ticker(activo.ticker)
        precio = ticker_yf.info.get('currentPrice')
        
        resultado.append(ActivoResponse(
            id=activo.id,
            ticker=activo.ticker,
            nombre=activo.nombre,
            cantidad=cantidad,
            precio=precio,
            compras=compras
        ))
    return resultado


@router.get("/resumen", response_model=CarteraResumenResponse)
def resumen_catera(db: Session = Depends(get_db), usuario = Depends(obtener_usuario_actual)) -> CarteraResumenResponse:
    activos = db.query(models.Activo).count()
    compras = db.query(models.Compra).count()

    return CarteraResumenResponse(
    total_activos=activos,
    total_compras=compras
    )


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
def obtener_activo(ticker: str, db: Session = Depends(get_db), usuario = Depends(obtener_usuario_actual)):
    activo = db.query(models.Activo).filter(models.Activo.ticker == ticker, models.Activo.usuario_id == usuario.id).first()
    if activo is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    return activo

@router.get("/activos/resumen")
def resumen(db: Session = Depends(get_db), usuario = Depends(obtener_usuario_actual)):
    activos = db.query(models.Activo).filter(models.Activo.usuario_id == usuario.id).count()
    compras = db.query(models.Compra).filter(models.Compra.activo_id.in_(
        db.query(models.Activo.id).filter(models.Activo.usuario_id == usuario.id)
    )).count()
    return {
        "numero_activos": activos,
        "numero_compras": compras
    }

@router.get("/activos/{ticker}/rendimiento", response_model=RendimientoResponse)
def rendimiento_activo(ticker: str, db: Session = Depends(get_db), usuario = Depends(obtener_usuario_actual)):
    activo = db.query(models.Activo).filter(models.Activo.ticker == ticker, models.Activo.usuario_id == usuario.id).first()
    if activo is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")

    total_invertido = db.query(
        func.sum(models.Compra.precio * models.Compra.cantidad * models.Compra.tipo_cambio)
    ).filter(
        models.Compra.activo_id == activo.id
    ).scalar()
    total_invertido = total_invertido or 0

    ticker_yf = yf.Ticker(ticker)
    precio_actual = ticker_yf.info.get('currentPrice')
    if precio_actual is None:
        raise HTTPException(status_code=502, detail="No se pudo obtener el precio actual")

    total_acciones = db.query(
        func.sum(models.Compra.cantidad)
    ).filter(
        models.Compra.activo_id == activo.id
    ).scalar()
    total_acciones = total_acciones or 0

    valor_actual = precio_actual*total_acciones

    ganancia = valor_actual-total_invertido

    if total_invertido > 0:
        porcentaje = (ganancia / total_invertido) * 100
    else:
        porcentaje = 0

    return RendimientoResponse(
        ticker = ticker,
        total_invertido=total_invertido,
        valor_actual=valor_actual,
        ganancia=ganancia,
        porcentaje=porcentaje
    )

@router.get("/activos/comparacion/{ticker1}/{ticker2}", response_model=ComparacionResponse)
def comparar_activos(ticker1:str, ticker2:str, db: Session = Depends(get_db), usuario = Depends(obtener_usuario_actual)):
    activo1 = db.query(models.Activo).filter(models.Activo.ticker == ticker1, models.Activo.usuario_id == usuario.id).first()
    if activo1 is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    activo2 = db.query(models.Activo).filter(models.Activo.ticker == ticker2, models.Activo.usuario_id == usuario.id).first()
    if activo2 is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")

    ticker_yf1 = yf.Ticker(ticker1)
    precio_actual1 = ticker_yf1.info.get('currentPrice')

    ticker_yf2 = yf.Ticker(ticker2)
    precio_actual2 = ticker_yf2.info.get('currentPrice')

    total_invertido1 = db.query(
        func.sum(models.Compra.precio * models.Compra.cantidad * models.Compra.tipo_cambio)
    ).filter(
        models.Compra.activo_id == activo1.id
    ).scalar()
    total_invertido1 = total_invertido1 or 0

    total_invertido2 = db.query(
        func.sum(models.Compra.precio * models.Compra.cantidad * models.Compra.tipo_cambio)
    ).filter(
        models.Compra.activo_id == activo2.id
    ).scalar()
    total_invertido2 = total_invertido2 or 0

    cantidad_acciones1 = db.query(
        func.sum(models.Compra.cantidad)
    ).filter(
        models.Compra.activo_id == activo1.id
    ).scalar()
    cantidad_acciones1 = cantidad_acciones1 or 0

    cantidad_acciones2 = db.query(
        func.sum(models.Compra.cantidad)
    ).filter(
        models.Compra.activo_id == activo2.id
    ).scalar()
    cantidad_acciones2 = cantidad_acciones2 or 0

    total_dividendos1 = db.query(
        func.sum(models.Dividendo.div_origen * models.Dividendo.cambio_nominal * (1 - models.Dividendo.impuesto / 100))
    ).filter(models.Dividendo.activo_id == activo1.id).scalar() or 0

    cantidad_dividendos1 = db.query(models.Dividendo).filter(
        models.Dividendo.activo_id == activo1.id
    ).count()

    total_dividendos2 = db.query(
        func.sum(models.Dividendo.div_origen * models.Dividendo.cambio_nominal * (1 - models.Dividendo.impuesto / 100))
    ).filter(models.Dividendo.activo_id == activo2.id).scalar() or 0

    cantidad_dividendos2 = db.query(models.Dividendo).filter(
        models.Dividendo.activo_id == activo2.id
    ).count()

    return ComparacionResponse(
        ticker1 = ticker1,
        precio_actual1 = precio_actual1,
        total_invertido1 = total_invertido1,
        cantidad_acciones1 = cantidad_acciones1,
        total_dividendos1 = total_dividendos1,
        cantidad_dividendos1 = cantidad_dividendos1,
        ticker2 = ticker2,
        precio_actual2 = precio_actual2,
        total_invertido2 = total_invertido2,
        cantidad_acciones2 = cantidad_acciones2,
        total_dividendos2 = total_dividendos2,
        cantidad_dividendos2 = cantidad_dividendos2,
    )
        


@router.post("/activos")
def crear_activo(activo: Activo, db: Session = Depends(get_db), usuario = Depends(obtener_usuario_actual), background_tasks: BackgroundTasks = BackgroundTasks()):
    nuevo_activo = models.Activo(**activo.model_dump(), usuario_id=usuario.id)
    db.add(nuevo_activo)
    db.commit()
    db.refresh(nuevo_activo)
    
    background_tasks.add_task(registrar_log, nuevo_activo.ticker, nuevo_activo.nombre)
    
    return nuevo_activo

@router.post("/preguntar")
async def preguntar_ia(pregunta: Pregunta):
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=pregunta.texto
    )
    return {"respuesta": response.text}

@router.post("/preguntar-activo")
async def preguntar_sobre_activo(data: PreguntaActivo, db: Session = Depends(get_db), usuario = Depends(obtener_usuario_actual)):
    activo = db.query(models.Activo).filter(models.Activo.ticker == data.ticker, models.Activo.usuario_id == usuario.id).first()
    if activo is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    
    compras = db.query(models.Compra).filter(models.Compra.activo_id == activo.id).all()
    cantidad = sum(c.cantidad for c in compras) if compras else 0
    
    ticker_yf = yf.Ticker(activo.ticker)
    precio = ticker_yf.info.get('currentPrice', 'no disponible')
    dividendo_anual = ticker_yf.info.get('dividendRate', 'no disponible')
    
    compras_texto = "\n".join([
        f"  - {c.cantidad} acciones a {c.precio}$ el {c.fecha_compra}"
        for c in compras
    ])
    
    contexto = f"""
    Tengo el siguiente activo en mi cartera:
    - Ticker: {activo.ticker}
    - Nombre: {activo.nombre}
    - Precio actual: {precio}$
    - Cantidad total: {cantidad}
    - Dividendo anual por acción: {dividendo_anual}$
    
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
def actualizar_activo(ticker: str, activo_nuevo: Activo, db: Session = Depends(get_db), usuario = Depends(obtener_usuario_actual)):
    activo = db.query(models.Activo).filter(models.Activo.ticker == ticker, models.Activo.usuario_id == usuario.id).first()
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
def eliminar_activo(ticker: str, db: Session = Depends(get_db), usuario = Depends(obtener_usuario_actual)):
    activo = db.query(models.Activo).filter(models.Activo.ticker == ticker, models.Activo.usuario_id == usuario.id).first()
    if activo is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    db.delete(activo)
    db.commit()
    return {"detalle": f"{ticker} borrado exitosamente"}