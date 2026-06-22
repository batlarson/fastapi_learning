from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from database import Base


class Activo(Base):
    __tablename__ = "activos"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(5), index=True)
    nombre = Column(String(50))


class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True)
    activo_id = Column(Integer, ForeignKey("activos.id"))
    fecha_compra = Column(String)
    precio = Column(Numeric(10, 2))
    cantidad = Column(Numeric(15, 8))
    tipo_cambio = Column(Numeric(10, 6))

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(255))
