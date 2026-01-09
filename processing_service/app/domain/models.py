from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ArticleAttributes(BaseModel):
    id: str
    title: str
    summary: str
    cleaned_summary: Optional[str] = None
    embedding: Optional[List[float]] = None
    categories: List[str]
    published: datetime
    # Outros campos herdados do raw...

    # Validator opcional para garantir dimensão correta do modelo (ex: MiniLM = 384)
    # @field_validator('embedding')
    # def check_embedding_dim(cls, v):
    #     if v and len(v) != 384: raise ValueError("Invalid embedding dimension")
    #     return v
