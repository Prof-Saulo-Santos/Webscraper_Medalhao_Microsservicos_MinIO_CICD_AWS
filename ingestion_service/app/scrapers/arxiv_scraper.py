import asyncio
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List

from app.domain.article import Article, Author
from app.core.logger import logger


class ArxivScraper:
    async def fetch_articles(
        self, query: str, max_results: int, start: int = 0
    ) -> List[Article]:

        url = (
            "https://arxiv.org/search/"
            f"?query={query}"
            "&searchtype=all"
            "&abstracts=show"
            "&order=-announced_date_first"
            f"&size={max_results}"
            f"&start={start}"
        )

        headers = {
            "User-Agent": "IngestionService/1.0 (contact: admin@example.com)"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)

        # ===============================
        # Tratamento correto de erros HTTP
        # ===============================

        if response.status_code == 429:
            logger.error(
                "Rate limit do arXiv atingido (HTTP 429). "
                "Aguardando antes de nova tentativa."
            )
            await asyncio.sleep(5) # Espera 5 segundos antes de nova tentativa, para evitar bloqueios. 
            raise RuntimeError("ARXIV_RATE_LIMIT")

        if response.status_code != 200:
            logger.error(
                f"Erro HTTP ao acessar arXiv: {response.status_code}"
            )
            raise RuntimeError(f"ARXIV_HTTP_{response.status_code}")

        # ===============================
        # Parse do HTML
        # ===============================

        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.select("li.arxiv-result")[:max_results]

        if not results:
            logger.warning(
                "Nenhum resultado encontrado. "
                "Query inválida ou layout do arXiv alterado."
            )
            return []

        articles: List[Article] = []
        processed_count = 0

        for result in results:
            try:
                # Título
                title_elem = result.select_one("p.title")
                title = title_elem.get_text(strip=True) if title_elem else "Sem título"

                # ID do arXiv
                arxiv_id = None

                pdf_link_elem = result.select_one("p.list-pdf a[href*='/pdf/']")
                if pdf_link_elem:
                    href = pdf_link_elem["href"]
                    pdf_link = (
                        href if href.startswith("http") else f"https://arxiv.org{href}"
                    )
                    arxiv_id = pdf_link.split("/")[-1].replace(".pdf", "")
                else:
                    pdf_link = None

                page_link_elem = result.select_one("a[href*='/abs/']")
                if page_link_elem:
                    href = page_link_elem["href"]
                    link = (
                        href if href.startswith("http") else f"https://arxiv.org{href}"
                    )
                    if not arxiv_id:
                        arxiv_id = link.split("/")[-1]
                else:
                    link = ""

                if not arxiv_id:
                    arxiv_id = f"unknown_{start + processed_count}"

                # Autores
                authors = [
                    Author(name=a.get_text(strip=True))
                    for a in result.select("p.authors a")
                ]

                # Abstract
                abstract_elem = result.select_one("span.abstract-full")
                summary = (
                    abstract_elem.get_text(separator=" ", strip=True)
                    if abstract_elem
                    else ""
                )

                # Datas
                date_span = result.find(
                    "span", string=lambda t: t and "Submitted" in t
                )

                if date_span:
                    try:
                        date_text = date_span.get_text(strip=True)
                        parts = date_text.split(";")
                        published = datetime.strptime(
                            parts[0].replace("Submitted ", "").strip(),
                            "%d %B %Y",
                        )
                        if len(parts) > 1:
                            updated = datetime.strptime(
                                parts[1].replace("updated ", "").strip(),
                                "%d %B %Y",
                            )
                        else:
                            updated = published
                    except Exception:
                        logger.warning(
                            f"Falha ao parsear datas: '{date_text}'. "
                            "Usando data atual."
                        )
                        published = updated = datetime.now()
                else:
                    published = updated = datetime.now()

                # Categorias
                categories = [
                    tag.get_text(strip=True)
                    for tag in result.select("span.primary-subject, span.subjects")
                ]

                articles.append(
                    Article(
                        id=arxiv_id,
                        title=title,
                        authors=authors,
                        summary=summary,
                        published=published,
                        updated=updated,
                        categories=categories or [query],
                        link=link,
                        pdf_link=pdf_link,
                    )
                )

                processed_count += 1

            except Exception as e:
                logger.error(f"Erro ao processar artigo: {e}")
                continue

        return articles
