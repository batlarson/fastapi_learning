from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import sys
sys.path.insert(0, '..')
from auth import crear_token, verificar_password, hashear_password
from database import get_db
import models
from pydantic import BaseModel

router = APIRouter()

class UsuarioCreate(BaseModel):
    username: str
    password: str


@router.post("/registro")
def registrar(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    existe = db.query(models.Usuario).filter(models.Usuario.username == usuario.username).first()
    if existe:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    nuevo_usuario = models.Usuario(
        username=usuario.username,
        password_hash=hashear_password(usuario.password)
    )
    db.add(nuevo_usuario)
    db.commit()
    return {"mensaje": f"Usuario {usuario.username} creado correctamente"}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.username == form_data.username).first()
    if not usuario or not verificar_password(form_data.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = crear_token({"sub": usuario.username})
    return {"access_token": token, "token_type": "bearer"}