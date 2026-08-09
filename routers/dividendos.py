from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from auth import obtener_usuario_actual
import models
from .activos import registrar_log




router = APIRouter()



class DividendoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    ticker: str
    fecha_pago: str
    dividendo: Decimal | None = None

class DividendoCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    activo_id: int
    fecha_pago: str
    div_origen: Decimal | None = None
    cambio_nominal: Decimal | None = None
    impuesto: int

class DividendoResumenResponse(BaseModel):
    numero_dividendos: int
    total_dividendos: float | None = None


@router.get("/dividendos/{ticker}", response_model=list[DividendoResponse])
def listar_dividendos(ticker: str, db: Session = Depends(get_db), usuario = Depends(obtener_usuario_actual)):
    activo = db.query(models.Activo).filter(models.Activo.ticker == ticker, models.Activo.usuario_id == usuario.id).first()
    if activo is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    dividendos = db.query(models.Dividendo).filter(models.Dividendo.activo_id == activo.id).all()
    resultado = []
    for div in dividendos:
        dividendo = div.div_origen * div.cambio_nominal * (1 - div.impuesto / 100)
           
            
        resultado.append(DividendoResponse(
            id=activo.id,
            ticker=activo.ticker,
            fecha_pago=div.fecha_pago,
            dividendo=dividendo,

        ))
    return resultado

@router.get("/dividendos/resumen", response_model=DividendoResumenResponse)
def resumen(db: Session = Depends(get_db), usuario = Depends(obtener_usuario_actual)):
    num_dividendos = db.query(models.Dividendo).filter(
        models.Dividendo.activo_id.in_(
            db.query(models.Activo.id).filter(models.Activo.usuario_id == usuario.id)
        )
    ).count()

    total_dividendos = db.query(func.sum(models.Dividendo.div_origen)).filter(
        models.Dividendo.activo_id.in_(
            db.query(models.Activo.id).filter(models.Activo.usuario_id == usuario.id)
        )
    ).scalar()

    return DividendoResumenResponse(
        numero_dividendos=num_dividendos,
        total_dividendos=total_dividendos
    )

@router.post("/dividendos", response_model=DividendoResponse)
def crear_dividendo(div : DividendoCreate, db: Session = Depends(get_db), usuario = Depends(obtener_usuario_actual),  background_tasks: BackgroundTasks = BackgroundTasks()):
    activo = db.query(models.Activo).filter(models.Activo.id == div.activo_id, models.Activo.usuario_id == usuario.id).first()
    if activo is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")

    nuevo_dividendo = models.Dividendo(**div.model_dump())
    div_real = nuevo_dividendo.div_origen * nuevo_dividendo.cambio_nominal * (1 - nuevo_dividendo.impuesto / Decimal('100'))

    db.add(nuevo_dividendo)
    db.commit()
    db.refresh(nuevo_dividendo)
    
    background_tasks.add_task(registrar_log, nuevo_dividendo.div_origen, nuevo_dividendo.fecha_pago)
    
    return DividendoResponse(
        id=nuevo_dividendo.id,
        ticker=activo.ticker,
        fecha_pago=div.fecha_pago,
        dividendo=div_real
    )

@router.put("/dividendos/{dividendo_id}")
def actualizar_dividendo(dividendo_id: int, dividendo_nuevo: DividendoCreate, db: Session = Depends(get_db), usuario = Depends(obtener_usuario_actual)):
    dividendo = db.query(models.Dividendo).filter(models.Dividendo.id == dividendo_id).first()
    if  dividendo is None:
        raise HTTPException(status_code=404, detail="Dividendo no encontrado")

    activo = db.query(models.Activo).filter(
        models.Activo.id == dividendo.activo_id,
        models.Activo.usuario_id == usuario.id
    ).first()
    if activo is None:
        raise HTTPException(status_code=403, detail="No tienes permiso")
    
    dividendo.fecha_pago = dividendo_nuevo.fecha_pago
    dividendo.div_origen = dividendo_nuevo.div_origen
    dividendo.cambio_nominal = dividendo_nuevo.cambio_nominal
    dividendo.impuesto = dividendo_nuevo.impuesto

    
    db.commit()
    db.refresh(dividendo)
    return dividendo

@router.delete("/dividendos/{dividendo_id}")
def eliminar_dividendo(dividendo_id: int, db: Session = Depends(get_db), usuario = Depends(obtener_usuario_actual)):
    dividendo = db.query(models.Dividendo).filter(models.Dividendo.id == dividendo_id).first()
    if  dividendo is None:
        raise HTTPException(status_code=404, detail="Dividendo no encontrado")

    activo = db.query(models.Activo).filter(
        models.Activo.id == dividendo.activo_id,
        models.Activo.usuario_id == usuario.id
    ).first()
    if activo is None:
        raise HTTPException(status_code=403, detail="No tienes permiso")
    
    db.delete(dividendo)
    db.commit()
    return {"detalle": f"Dividendo {dividendo_id} borrado exitosamente"}