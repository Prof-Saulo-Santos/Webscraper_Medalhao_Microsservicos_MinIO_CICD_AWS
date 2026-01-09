from app.domain.repository import RepositoryProtocol
from app.domain.scraper import ScraperProtocol
from app.core.logger import logger
import random
import asyncio
from datetime import datetime


class IngestionService:
    def __init__(self, repository: RepositoryProtocol, scraper: ScraperProtocol):
        self.repo = repository
        self.scraper = scraper

    async def run(self, query: str, max_results: int = 50):
        logger.info(
            f"Iniciando ingestão de até {max_results} artigos para query='{query}'..."
        )

        collected_count = 0
        start = 0
        batch_size = 50  # Padrão do arXiv

        while collected_count < max_results:
            # Garante que não pede mais do que o batch permite ou o que falta
            logger.info(f"Buscando página iniciando em {start}...")

            # Limita a busca ao tamanho do batch
            articles = await self.scraper.fetch_articles(query, batch_size, start=start)

            if not articles:
                logger.info("Nenhum artigo retornado. Encerrando busca.")
                break

            count_saved = 0
            for article in articles:
                payload = {
                    "ingestion_timestamp": datetime.now().isoformat(),
                    "ingestion_source": "arxiv_html",
                    "search_query": query,
                    "article_data": article.model_dump(mode="json"),
                }
                await self.repo.save_json(f"{article.id}.json", payload)
                count_saved += 1

            collected_count += count_saved
            start += len(articles)

            logger.info(
                f"Página processada. Coletados: {collected_count}/{max_results}"
            )

            # Se veio menos artigos que o batch, significa que acabou a fonte
            if len(articles) < batch_size:
                break

            # Anti-Ban: Pausa se ainda não acabou
            if collected_count < max_results:
                wait_time = random.uniform(80.0, 90.0)
                logger.info(
                    f"Aguardando {wait_time:.2f}s para próxima página (Anti-Ban)..."
                )
                await asyncio.sleep(wait_time)

        logger.info(f"Ingestão concluída. Total coletado: {collected_count}")
