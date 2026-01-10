from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router
from app.core.storage import initialize_buckets
from app.core.config import settings
from app.services.ingestion_service import IngestionService
from app.repositories.s3_repository import S3Repository
from app.scrapers.arxiv_scraper import ArxivScraper
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_buckets()
    
    if settings.RUN_ON_STARTUP:
        print("🚀 RUN_ON_STARTUP=True. Iniciando Job de Ingestão...")
        service = IngestionService(repository=S3Repository(), scraper=ArxivScraper())
        # Roda em background para não bloquear o startup do Uvicorn (opcional, mas bom pra healthcheck)
        asyncio.create_task(service.run(query="Isotretinoina", max_results=50))
    
    yield
    # Shutdown


app = FastAPI(
    title="Ingestion Service - arXiv Bronze",
    description="Microserviço de ingestão de artigos do arXiv para camada Bronze",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)
