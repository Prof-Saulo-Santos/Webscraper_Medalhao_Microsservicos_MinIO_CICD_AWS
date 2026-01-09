import json
import boto3
import asyncio
from app.core.config import settings
from app.core.logger import logger


class S3Repository:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT if settings.USE_S3 else None,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket = settings.S3_BUCKET_NAME

    async def save_json(self, key: str, data: dict):
        try:
            await asyncio.to_thread(
                self.client.put_object,
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
                ContentType="application/json",
            )
            logger.info(f"Objeto salvo com sucesso: {key}")
        except Exception as e:
            logger.error(f"Erro ao salvar objeto {key}: {e}")
