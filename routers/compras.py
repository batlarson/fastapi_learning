from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
import sys
sys.path.insert(0, '..')
import models
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from auth import obtener_usuario_actual


router = APIRouter()

class Compra(BaseModel):
    activo_id: int
    fecha_compra: str
    precio: Decimal
    cantidad: Decimal
    tipo_cambio: Decimal

class CompraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo_id: int
    fecha_compra: str
    precio: Decimal
    cantidad: Decimal
    tipo_cambio: Decimal


@router.get("/compras/{ticker}", response_model=CompraResponse)
def listar_compras(ticker: str, db: Session = Depends(get_db), usuario = Depends(obtener_usuario_actual)):
    activo = db.query(models.Activo).filter(models.Activo.ticker == ticker, models.Activo.usuario_id == usuario.id).first()
    if activo is None:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    compras = db.query(models.Compra).filter(models.Compra.activo_id == activo.id).all()
    return compras

@router.post("/compras", response_model=CompraResponse)
def crear_compra(compra: Compra, db: Session = Depends(get_db)):
    nueva_compra = models.Compra(**compra.model_dump())
    db.add(nueva_compra)
    db.commit()
    db.refresh(nueva_compra)
    return nueva_compra