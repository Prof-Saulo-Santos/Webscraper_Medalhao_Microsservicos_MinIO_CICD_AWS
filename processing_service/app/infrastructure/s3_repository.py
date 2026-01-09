import json
from typing import List
import boto3
from app.domain.ports import RepositoryProtocol
from app.domain.models import ArticleAttributes
from app.core.config import settings


class S3Repository(RepositoryProtocol):
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self._ensure_buckets_exist()

    def _ensure_buckets_exist(self):
        for bucket in [settings.S3_BUCKET_BRONZE, settings.S3_BUCKET_SILVER]:
            try:
                self.s3.head_bucket(Bucket=bucket)
            except self.s3.exceptions.ClientError:
                # Bucket likely missing, try to create
                try:
                    self.s3.create_bucket(Bucket=bucket)
                    print(f"Bucket {bucket} created.")
                except Exception as e:
                    print(f"Failed to create bucket {bucket}: {e}")

    async def list_unprocessed_files(self) -> List[str]:
        # 1. Listar tudo no Bronze (Paginação s3.list_objects_v2 omitida para brevidade)
        bronze_objs = self.s3.list_objects_v2(Bucket=settings.S3_BUCKET_BRONZE).get(
            "Contents", []
        )
        bronze_keys = {obj["Key"] for obj in bronze_objs}

        # 2. Listar tudo no Silver
        silver_objs = self.s3.list_objects_v2(Bucket=settings.S3_BUCKET_SILVER).get(
            "Contents", []
        )
        silver_ids = {obj["Key"].replace(".json", "") for obj in silver_objs}

        # 3. Set Difference (O(1) lookup)
        # Se bronze tem "folder/123.json", extraímos "123" para comparar.
        unprocessed = []
        for key in bronze_keys:
            article_id = key.split("/")[-1].replace(".json", "")
            if article_id not in silver_ids:
                unprocessed.append(key)

        return unprocessed

    async def get_raw_article(self, file_key: str) -> dict:
        response = self.s3.get_object(Bucket=settings.S3_BUCKET_BRONZE, Key=file_key)
        return json.loads(response["Body"].read())

    async def save_processed_article(self, article: ArticleAttributes) -> None:
        key = f"{article.id}.json"
        self.s3.put_object(
            Bucket=settings.S3_BUCKET_SILVER,
            Key=key,
            Body=article.model_dump_json(indent=2),
            ContentType="application/json",
        )

    async def exists_in_silver(self, article_id: str) -> bool:
        # Esta implementação é O(1) se o bucket for pequeno, mas O(N) para listar tudo.
        # A list_unprocessed_files já faz uma checagem mais eficiente para o batch.
        # Para checagem individual, pode-se tentar get_object e capturar ClientError.
        try:
            self.s3.head_object(
                Bucket=settings.S3_BUCKET_SILVER, Key=f"{article_id}.json"
            )
            return True
        except self.s3.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise  # Re-raise other errors
