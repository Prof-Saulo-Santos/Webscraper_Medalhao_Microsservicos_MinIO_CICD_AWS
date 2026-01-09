# tests/test_service.py
import pytest
from unittest.mock import AsyncMock, Mock
from app.services.processor_service import ProcessingService
from app.domain.models import ArticleAttributes


@pytest.mark.asyncio
async def test_processing_service_flow():
    # Mocks
    mock_repo = AsyncMock()
    mock_cleaner = Mock()
    mock_embedder = Mock()

    # Configuração
    mock_repo.exists_in_silver.return_value = False
    mock_repo.get_raw_article.return_value = {
        "article_data": {
            "id": "123",
            "title": "Test",
            "summary": "Raw summary",
            "categories": ["cs.AI"],
            "published": "2024-01-01",
        }
    }
    mock_cleaner.clean_text.return_value = "cleaned summary"
    mock_embedder.generate_embedding.return_value = [0.1, 0.2]

    service = ProcessingService(mock_repo, mock_cleaner, mock_embedder)

    # Execução
    await service.process_one_file("123.json")

    # Verificação
    # 1. Garante que processou
    mock_cleaner.clean_text.assert_called_with("Raw summary")
    mock_embedder.generate_embedding.assert_called_with("cleaned summary")

    # 2. Garante que salvou
    mock_repo.save_processed_article.assert_called_once()
    saved_article = mock_repo.save_processed_article.call_args[0][0]
    assert saved_article.cleaned_summary == "cleaned summary"
    assert saved_article.embedding == [0.1, 0.2]
