import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from app.services.search_engine import SearchEngine


@pytest.fixture
def mock_s3_data():
    return [
        {
            "id": "1",
            "title": "Paper A",
            "summary": "Sum A",
            "embedding": [1.0, 0.0, 0.0],
            "categories": ["cs.AI"],
        },
        {
            "id": "2",
            "title": "Paper B",
            "summary": "Sum B",
            "embedding": [0.0, 1.0, 0.0],
            "categories": ["cs.CL"],
        },
    ]


@patch("app.services.search_engine.boto3")
@patch("app.services.search_engine.AutoTokenizer")
@patch("app.services.search_engine.AutoModel")
def test_search_engine_logic(
    mock_model_cls, mock_tokenizer_cls, mock_boto, mock_s3_data
):
    # 1. Setup Mocks
    # Mock do S3
    mock_s3_client = Mock()
    mock_boto.client.return_value = mock_s3_client

    # Simula listagem de arquivos
    mock_s3_client.list_objects_v2.return_value = {
        "Contents": [{"Key": "1.json"}, {"Key": "2.json"}]
    }

    # Simula retorno do conteúdo dos arquivos (streaming body)
    def get_object_side_effect(Bucket, Key):
        import json
        from io import BytesIO

        data = mock_s3_data[0] if Key == "1.json" else mock_s3_data[1]
        body = BytesIO(json.dumps(data).encode("utf-8"))
        return {"Body": body}

    mock_s3_client.get_object.side_effect = get_object_side_effect

    # Mock do BERT (evitar download/loading pesado)
    mock_tokenizer = Mock()
    mock_model = Mock()
    mock_tokenizer_cls.from_pretrained.return_value = mock_tokenizer
    mock_model_cls.from_pretrained.return_value = mock_model

    # Simula output do modelo (Tensor)
    import torch

    # SETUP SIMPLIFICADO: Mockar a funçao tokenizer para retornar dict
    mock_tokenizer.return_value = {
        "input_ids": torch.tensor([[1]]),
        "attention_mask": torch.tensor([[1]]),
    }

    # Mock output do modelo: last_hidden_state com shape [1, 1, 3]
    # Se a query for [1, 0, 0], score com Paper A (1,0,0) será 1.0.
    mock_output = Mock()
    mock_output.last_hidden_state = torch.tensor([[[1.0, 0.0, 0.0]]])
    mock_model.return_value = mock_output

    # 2. Execução
    engine = SearchEngine()
    # Force load (bypass streamlit cache decoration issues in raw test if needed,
    # but mocks handle imports usually. If @st.cache fails in test, mock st)
    with patch("app.services.search_engine.st"):
        results = engine.search("fake query", top_k=2)

    # 3. Asserts
    assert len(results) == 2
    # Paper A deve ser o primeiro pois query [1,0,0] == Paper A [1,0,0] (Score 1.0)
    assert results[0]["id"] == "1"
    assert results[0]["score"] > 0.9

    # Paper B [0,1,0] deve ter score baixo com query [1,0,0] (Ortogonal = 0.0)
    assert results[1]["id"] == "2"
    assert results[1]["score"] < 0.1
