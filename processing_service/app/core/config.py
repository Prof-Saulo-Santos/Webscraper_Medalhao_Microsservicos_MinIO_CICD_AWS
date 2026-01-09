from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    USE_S3: bool = True
    S3_ENDPOINT: str = "http://minio:9000"
    S3_BUCKET_BRONZE: str = "arxiv-bronze"
    S3_BUCKET_SILVER: str = "arxiv-silver"
    AWS_ACCESS_KEY_ID: str = "minioadmin"
    AWS_SECRET_ACCESS_KEY: str = "minioadmin"
    AWS_REGION: str = "us-east-1"
    MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
