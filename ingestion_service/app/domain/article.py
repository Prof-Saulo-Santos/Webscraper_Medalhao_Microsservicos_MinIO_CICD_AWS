from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class Author(BaseModel):
    name: str

class Article(BaseModel):
    id: str
    title: str
    authors: List[Author]
    summary: str
    published: datetime
    updated: datetime
    categories: List[str]
    link: str
    pdf_link: Optional[str] = None
