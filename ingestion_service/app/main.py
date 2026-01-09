from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router
from app.core.storage import initialize_buckets


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_buckets()
    yield
    # Shutdown


app = FastAPI(
    title="Ingestion Service - arXiv Bronze",
    description="Microserviço de ingestão de artigos do arXiv para camada Bronze",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)
