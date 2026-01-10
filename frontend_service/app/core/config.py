from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações da aplicação seguindo o padrão '12-Factor App'.
    
    NOTA DE ESTUDO:
    O código usa variáveis de ambiente ("Environment Variables") para decidir onde conectar.
    * Se a variável S3_ENDPOINT existe (no seu PC local), ele usa MinIO.
    * Se ela não existe (na AWS), ele assume que é S3 real (None).
    
    É a mesma chave que abre duas portas diferentes dependendo de onde você está.
    """
    USE_S3: bool = True
    S3_ENDPOINT: Optional[str] = None
    S3_BUCKET_BRONZE: str = "arxiv-bronze"
    S3_BUCKET_SILVER: str = "arxiv-silver"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
