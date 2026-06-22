from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def crear_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    

    
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    payload = verificar_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return payload.get("sub")  # "sub" es donde guardamos el username

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hashear_password(password: str) -> str:
    """Hash a password using the configured passlib scheme.

    Uses the 'bcrypt_sha256' scheme (via passlib) to hash the provided password.
    Expects a str (text) password; returns a bcrypt-formatted hash string suitable
    for storage in a database.
    """
    return pwd_context.hash(password)

def verificar_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)