from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from fastapi import APIRouter, HTTPException, Depends
import models



router = APIRouter()

fotos_db = []


class FotoResponse(BaseModel):
    filename: str
    user_id:int
    url: str

class FotoCreate(BaseModel):
    filename: str

@router.get("/users/{user_id}/fotos")
def listar_fotos(user_id:int):
    return [foto for foto in fotos_db if foto.user_id == user_id]

@router.get("/users/{user_id}/fotos/{filename}")
def obtener_foto(user_id: int, filename: str):
    for foto in fotos_db:
        if foto.user_id == user_id and foto.filename == filename:
            return foto
    raise HTTPException(status_code=404, detail="Foto no encontrada")

@router.post("/users/{user_id}/fotos")
def subir_foto(user_id: int, foto: FotoCreate):
    nueva_foto = FotoResponse(
        filename=foto.filename,
        user_id=user_id,
        url=f"http://ejemplo.com/fotos/{user_id}/{foto.filename}"
    )
    fotos_db.append(nueva_foto)
    return nueva_foto

@router.delete("/users/{user_id}/fotos/{filename}")
def borrar_foto(user_id: int, filename: str):
    for foto in fotos_db:
        if foto.user_id == user_id and foto.filename == filename:
            fotos_db.remove(foto)
            return "Foto eliminada correctamente"
    raise HTTPException(status_code=404, detail="Foto no encontrada")