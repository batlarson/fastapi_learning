from fastapi import FastAPI
from database import Base, engine
import models
from routers import activos, compras, auth, fotos

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(activos.router)
app.include_router(compras.router)
app.include_router(fotos.router)
app.include_router(auth.router)










