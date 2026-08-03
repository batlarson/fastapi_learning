from fastapi import FastAPI
from database import Base, engine
import models
from routers import activos, compras, auth, fotos, dividendos
import time

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = round(time.time() - start, 3)
        print(f"{request.method} {request.url.path} → {response.status_code} ({duration}s)")
        return response

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

app.include_router(activos.router)
app.include_router(compras.router)
app.include_router(dividendos.router)
app.include_router(fotos.router)
app.include_router(auth.router)



