from fastapi import APIRouter, Query
from app.services.ingestion_service import IngestionService
from app.repositories.s3_repository import S3Repository
from app.scrapers.arxiv_scraper import ArxivScraper

router = APIRouter()


@router.get("/health", status_code=200)
def health_check():
    return {"status": "ok"}


@router.post("/ingest")
async def ingest(
    query: str = Query("cs.CL", description="Termo de busca no arXiv"),
    max_results: int = Query(
        50, description="Máximo de artigos a ingerir (paginação automática)"
    ),
):
    service = IngestionService(repository=S3Repository(), scraper=ArxivScraper())
    await service.run(query=query, max_results=max_results)
    return {
        "status": "ok",
        "message": f"Ingestão concluída para query='{query}' (até {max_results} resultados)",
    }
