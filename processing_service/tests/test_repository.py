# tests/test_repository.py
import pytest
import boto3
from moto import mock_aws
from app.infrastructure.s3_repository import S3Repository
from app.core.config import settings


from unittest.mock import patch


@pytest.fixture
def s3_mock():
    with mock_aws():
        # Patch S3_ENDPOINT to None so S3Repository uses standard AWS URLs (intercepted by moto)
        with patch.object(settings, "S3_ENDPOINT", None):
            # Setup do ambiente fake
            s3 = boto3.client("s3", region_name="us-east-1")
            s3.create_bucket(Bucket=settings.S3_BUCKET_BRONZE)
            s3.create_bucket(Bucket=settings.S3_BUCKET_SILVER)
            yield s3


@pytest.mark.asyncio
async def test_repo_exists_silver(s3_mock):
    repo = S3Repository()
    # Verifica inexistência
    assert await repo.exists_in_silver("fake_id") == False

    # Cria arquivo fake na silver e verifica
    s3_mock.put_object(Bucket=settings.S3_BUCKET_SILVER, Key="exist.json", Body="{}")
    assert await repo.exists_in_silver("exist") == True
