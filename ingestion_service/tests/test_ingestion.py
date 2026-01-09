import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.ingestion_service import IngestionService

MOCK_HTML = """
<li class="arxiv-result">
    <p class="title">Fake Article</p>
    <span class="abstract-full">Fake Summary</span>
    <p class="authors"><a href="#">Fake Author</a></p>
    <p class="list-pdf"><a href="/pdf/1234.5678">pdf</a></p>
    <span class="primary-subject">cs.CL</span>
</li>
"""


@pytest.fixture(autouse=True)
def mock_sleep():
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock:
        yield mock


@pytest.mark.asyncio
async def test_ingestion_success_flow(mock_sleep):
    # Setup Mock Scraper
    mock_scraper = AsyncMock()

    # Create a Fake Article object
    fake_article = MagicMock()
    fake_article.id = "1234.5678"
    fake_article.title = "Fake Article"
    fake_article.model_dump.return_value = {
        "id": "1234.5678",
        "title": "Fake Article",
        "authors": [{"name": "Fake"}],
        "summary": "Fake Summary",
    }

    mock_scraper.fetch_articles.return_value = [fake_article]

    # Setup Repo
    mock_repo = AsyncMock()

    service = IngestionService(repository=mock_repo, scraper=mock_scraper)
    await service.run(query="test", max_results=1)

    # Asserts
    mock_scraper.fetch_articles.assert_called_once()
    mock_repo.save_json.assert_called_once()

    args, _ = mock_repo.save_json.call_args
    filename, payload = args

    assert filename == "1234.5678.json"
    assert payload["ingestion_source"] == "arxiv_html"


@pytest.mark.asyncio
async def test_ingestion_scraper_failure(mock_sleep):
    # Setup Falha no Scraper
    mock_scraper = AsyncMock()
    mock_scraper.fetch_articles.side_effect = Exception("Scraper Failed")

    mock_repo = AsyncMock()
    service = IngestionService(repository=mock_repo, scraper=mock_scraper)

    # Deve propagar a exceção
    with pytest.raises(Exception):
        await service.run(query="test")
