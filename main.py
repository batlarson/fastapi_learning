from fastapi import FastAPI
from database import Base, engine
import models
from routers import activos, compras

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(activos.router)
app.include_router(compras.router)










