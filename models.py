from sqlalchemy import Column, Integer, String, Float
from database import Base

class Activo(Base):
    __tablename__ = "activos"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(5), index=True)
    nombre = Column(String(50))
    precio = Column(Float)
    cantidad = Column(Float, default=0.0)