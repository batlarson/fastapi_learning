from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database import Base



class Activo(Base):
    __tablename__ = "activos"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(5), index=True)
    nombre = Column(String(50))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    compras = relationship("Compra", back_populates="activo")
    dividendos = relationship("Dividendo", back_populates="activo")
    usuario = relationship("Usuario", back_populates="activos")


class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True)
    activo_id = Column(Integer, ForeignKey("activos.id"))
    fecha_compra = Column(String)
    precio = Column(Numeric(10, 2))
    cantidad = Column(Numeric(15, 8))
    tipo_cambio = Column(Numeric(10, 6))
    activo = relationship("Activo", back_populates="compras")

class Dividendo(Base):
    __tablename__ = "dividendos"
    id = Column(Integer, primary_key=True, index=True)
    activo_id = Column(Integer, ForeignKey("activos.id"))
    fecha_pago = Column(String)
    div_origen = Column(Numeric(12, 2))
    cambio_nominal = Column(Numeric(15, 8))
    impuesto = Column(Numeric(5, 2))
    activo = relationship("Activo", back_populates="dividendos")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(255))
    activos = relationship("Activo", back_populates="usuario")

