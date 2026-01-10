from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    USE_S3: bool = True
    S3_ENDPOINT: Optional[str] = None
    S3_BUCKET_NAME: str = "arxiv-bronze"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    # Feature Flag para rodar como Job (Batch) ao iniciar
    RUN_ON_STARTUP: bool = False
    SEARCH_QUERY: str = "Machine Learning"

settings = Settings()
