from app.domain.ports import RepositoryProtocol, CleanerProtocol, EmbedderProtocol
from app.domain.models import ArticleAttributes
from app.core.logger import logger
import asyncio


class ProcessingService:
    def __init__(
        self,
        repo: RepositoryProtocol,
        cleaner: CleanerProtocol,
        embedder: EmbedderProtocol,
    ):
        self.repo = repo
        self.cleaner = cleaner
        self.embedder = embedder

    async def process_one_file(self, file_key: str):
        # 0. Check de Idempotência (Evita reprocessamento)
        article_id = file_key.replace(".json", "")  # ou extrair do conteúdo
        if await self.repo.exists_in_silver(article_id):
            logger.info(f"Artigo {article_id} já processado. Pulando.")
            return

        logger.info(f"Processando arquivo: {file_key}")

        # 1. Leitura Bronze
        raw_data = await self.repo.get_raw_article(file_key)
        article_data = raw_data.get("article_data", {})

        # 2. Limpeza (CPU Bound - não bloquear loop)
        raw_summary = article_data.get("summary", "")
        cleaned_summary = await asyncio.to_thread(self.cleaner.clean_text, raw_summary)

        # 3. Embedding (CPU Bound & Heavy - Transformers bloqueia fortemente o loop)
        # Importante: asyncio.to_thread roda em thread separada, liberando o loop do FastAPI
        embedding = await asyncio.to_thread(
            self.embedder.generate_embedding, cleaned_summary
        )

        # 4. Montagem Objeto Silver
        article_silver = ArticleAttributes(
            **article_data, cleaned_summary=cleaned_summary, embedding=embedding
        )

        # 5. Persistência Silver
        await self.repo.save_processed_article(article_silver)
        logger.info(f"Artigo {article_silver.id} salvo na Silver.")


# Permite rodar como script standalone (Worker Mode)
if __name__ == "__main__":
    import argparse
    from app.infrastructure.s3_repository import S3Repository
    from app.infrastructure.regex_cleaner import RegexCleaner
    from app.infrastructure.bert_embedder import BERTEmbedder

    async def main():
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--limit", type=int, default=10, help="Limit files to process"
        )
        args = parser.parse_args()

        service = ProcessingService(S3Repository(), RegexCleaner(), BERTEmbedder())
        files = await service.repo.list_unprocessed_files()

        print(f"Starting batch processing of {min(args.limit, len(files))} files...")
        for f in files[: args.limit]:
            await service.process_one_file(f)
        print("Done.")

    asyncio.run(main())
