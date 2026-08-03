from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from auth import obtener_usuario_actual
import models




router = APIRouter()



class Dividendo(BaseModel):
    ticker: str
    fecha_pago: str
    div_origen: Decimal
    cambio_nominal: Decimal
    impuesto: int

class DividendoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    ticker: str
    fecha_pago: str
    dividendo: Decimal | None = None


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