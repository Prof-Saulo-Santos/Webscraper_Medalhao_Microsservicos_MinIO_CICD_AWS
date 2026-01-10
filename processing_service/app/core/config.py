from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    USE_S3: bool = True
    S3_ENDPOINT: Optional[str] = None
    S3_BUCKET_BRONZE: str = "arxiv-bronze"
    S3_BUCKET_SILVER: str = "arxiv-silver"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Feature Flag para rodar como Job (Batch) ao iniciar
    RUN_ON_STARTUP: bool = False

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
