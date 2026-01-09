from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    USE_S3: bool = True
    S3_ENDPOINT: str = "http://minio:9000"
    S3_BUCKET_NAME: str = "arxiv-bronze"
    AWS_ACCESS_KEY_ID: str = "minioadmin"
    AWS_SECRET_ACCESS_KEY: str = "minioadmin"
    AWS_REGION: str = "us-east-1"

settings = Settings()
