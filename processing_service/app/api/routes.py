from fastapi import APIRouter, Depends
from typing import Annotated
from app.infrastructure.s3_repository import S3Repository
from app.infrastructure.regex_cleaner import RegexCleaner
from app.infrastructure.bert_embedder import BERTEmbedder
from app.services.processor_service import ProcessingService

router = APIRouter()


# Dependency Factory
def get_processor_service():
    repo = S3Repository()
    cleaner = RegexCleaner()
    embedder = BERTEmbedder()
    return ProcessingService(repo, cleaner, embedder)


@router.post("/process_batch")
async def process_batch(
    service: Annotated[ProcessingService, Depends(get_processor_service)],
    limit: int = 10,
):
    files = (
        await service.repo.list_unprocessed_files()
    )  # Acesso direto ao repo injetado
    count = 0
    for f in files[:limit]:
        await service.process_one_file(f)
        count += 1

    return {"status": "ok", "processed": count}
