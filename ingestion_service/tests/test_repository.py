from unittest.mock import patch
import pytest
from app.repositories.s3_repository import S3Repository


@pytest.mark.asyncio
@patch("boto3.client")
async def test_save_json_calls_put_object(mock_boto):
    mock_client = mock_boto.return_value
    repo = S3Repository()

    data = {"key": "value"}
    await repo.save_json("test.json", data)

    mock_client.put_object.assert_called_once()
    call_args = mock_client.put_object.call_args[1]
    assert call_args["Bucket"] == "arxiv-bronze"
    assert call_args["Key"] == "test.json"
    assert b'{\n  "key": "value"\n}' in call_args["Body"]
