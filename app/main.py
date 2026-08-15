from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routers import categorias, ejercicios, intentos


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="API Ejercicios",
    description="Banco de ejercicios de programación para repasar antes de exámenes.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(categorias.router)
app.include_router(ejercicios.router)
app.include_router(intentos.router)


@app.get("/", tags=["info"])
def raiz():
    return {
        "api": "API Ejercicios",
        "docs": "/docs",
        "endpoints": ["/categorias", "/ejercicios", "/estadisticas"],
    }