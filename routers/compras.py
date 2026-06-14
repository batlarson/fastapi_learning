from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
import sys
sys.path.insert(0, '..')
import models
from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel
from decimal import Decimal

load_dotenv()


router = APIRouter()

class Compra(BaseModel):
    activo_id: int
    fecha_compra: str
    precio: Decimal
    cantidad: Decimal
    tipo_cambio: Decimal


@router.get("/compras/{activo_id}")
def listar_compras(activo_id: int, db: Session = Depends(get_db)):
    compras = db.query(models.Compra).filter(models.Compra.activo_id == activo_id).all()
    if compras is None:
        raise HTTPException(status_code=404, detail="Compras no encontradas")
    return db.query(models.Compra).all()

@router.post("/compras")
def crear_compra(compra: Compra, db: Session = Depends(get_db)):
    nueva_compra = models.Compra(**compra.model_dump())
    db.add(nueva_compra)
    db.commit()
    db.refresh(nueva_compra)
    return nueva_compra