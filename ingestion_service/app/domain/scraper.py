from typing import Protocol, List
from app.domain.article import Article


class ScraperProtocol(Protocol):
    async def fetch_articles(self, query: str, max_results: int, start: int = 0) -> List[Article]:
        """Busca artigos com base na query, paginação e offset."""
        ...
