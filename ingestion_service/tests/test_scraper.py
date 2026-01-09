import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.scrapers.arxiv_scraper import ArxivScraper

MOCK_HTML = """
<li class="arxiv-result">
    <p class="title">Fake Article</p>
    <span class="abstract-full">Fake Summary</span>
    <p class="authors"><a href="#">Fake Author</a></p>
    <p class="list-pdf"><a href="/pdf/1234.5678">pdf</a></p>
    <span class="primary-subject">cs.CL</span>
</li>
"""


@pytest.mark.asyncio
@patch("app.scrapers.arxiv_scraper.httpx.AsyncClient")
async def test_scraper_fetch_articles_success(mock_client_cls):
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = MOCK_HTML

    mock_client.__aenter__.return_value = mock_client
    mock_client.get.return_value = mock_response
    mock_client_cls.return_value = mock_client

    scraper = ArxivScraper()
    articles = await scraper.fetch_articles("test", 1)

    assert len(articles) == 1
    assert articles[0].title == "Fake Article"
    assert articles[0].id == "1234.5678"


@pytest.mark.asyncio
@patch("app.scrapers.arxiv_scraper.httpx.AsyncClient")
async def test_scraper_network_failure(mock_client_cls):
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.get.side_effect = Exception("Network Down")
    mock_client_cls.return_value = mock_client

    scraper = ArxivScraper()

    with pytest.raises(Exception):
        await scraper.fetch_articles("test", 1)
