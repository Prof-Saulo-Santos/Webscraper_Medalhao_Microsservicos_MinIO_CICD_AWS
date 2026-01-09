from unittest.mock import patch
from botocore.exceptions import ClientError
from app.core.storage import initialize_buckets


@patch("app.core.storage.settings")
@patch("app.core.storage.boto3.client")
def test_initialize_buckets_creates_if_missing(mock_boto, mock_settings):
    # Configurações do Mock
    mock_settings.USE_S3 = True
    mock_settings.S3_BUCKET_NAME = "arxiv-bronze"

    # Mock do Boto3 Client
    mock_client = mock_boto.return_value

    # Simula erro 404 (Not Found) ao checar o bucket
    error_response = {"Error": {"Code": "404", "Message": "Not Found"}}
    mock_client.head_bucket.side_effect = ClientError(error_response, "HeadBucket")

    # Executa a função
    initialize_buckets()

    # Verifica se create_bucket foi chamado corretamente
    mock_client.create_bucket.assert_called_once_with(Bucket="arxiv-bronze")


@patch("app.core.storage.settings")
@patch("app.core.storage.boto3.client")
def test_initialize_buckets_skips_if_exists(mock_boto, mock_settings):
    # Configurações do Mock
    mock_settings.USE_S3 = True
    mock_settings.S3_BUCKET_NAME = "arxiv-bronze"

    # Mock do Boto3 Client
    mock_client = mock_boto.return_value

    # Simula sucesso ao checar o bucket (sem exceção)
    mock_client.head_bucket.return_value = {}

    # Executa a função
    initialize_buckets()

    # Verifica se create_bucket NÃO foi chamado
    mock_client.create_bucket.assert_not_called()
