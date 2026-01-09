import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.ingestion_service import IngestionService
from app.domain.article import Article
from datetime import datetime


@pytest.mark.asyncio
async def test_pagination_loop_max_results():
    # Mock do Repositório
    mock_repo = AsyncMock()

    # Mock do Scraper
    mock_scraper = MagicMock()

    # Simula 2 páginas de resultados
    # 1ª chamada: 50 artigos
    page1 = [
        Article(
            id=f"1_{i}",
            title=f"Title {i}",
            authors=[],
            summary="",
            published=datetime.now(),
            updated=datetime.now(),
            categories=[],
            link="",
            pdf_link="",
        )
        for i in range(50)
    ]

    # 2ª chamada: 10 artigos (totalizando 60, mas o teste pede 60)
    page2 = [
        Article(
            id=f"2_{i}",
            title=f"Title {i}",
            authors=[],
            summary="",
            published=datetime.now(),
            updated=datetime.now(),
            categories=[],
            link="",
            pdf_link="",
        )
        for i in range(10)
    ]

    # Configura o side_effect para retornar page1, depois page2
    mock_scraper.fetch_articles = AsyncMock(side_effect=[page1, page2])

    service = IngestionService(repository=mock_repo, scraper=mock_scraper)

    # Mock do sleep para não esperar 80s de verdade
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        await service.run(query="test", max_results=60)

        # Verifica se chamou fetch_articles 2 vezes
        assert mock_scraper.fetch_articles.call_count == 2

        # Verifica os argumentos de cada chamada (start deve incrementar)
        calls = mock_scraper.fetch_articles.call_args_list
        assert calls[0].kwargs["start"] == 0
        assert calls[1].kwargs["start"] == 50

        # Verifica se save_json foi chamado 60 vezes
        assert mock_repo.save_json.call_count == 60

        # Verifica se o sleep foi chamado (anti-ban)
        assert mock_sleep.call_count >= 1


@pytest.mark.asyncio
async def test_pagination_stops_if_no_results():
    mock_repo = AsyncMock()
    mock_scraper = MagicMock()

    # Retorna vazio na primeira chamada
    mock_scraper.fetch_articles = AsyncMock(return_value=[])

    service = IngestionService(repository=mock_repo, scraper=mock_scraper)

    await service.run(query="test", max_results=100)

    assert mock_scraper.fetch_articles.call_count == 1
    assert mock_repo.save_json.call_count == 0
