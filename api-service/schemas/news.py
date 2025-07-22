from pydantic import BaseModel
from typing import List, Optional

class NewsSearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

class NewsArticle(BaseModel):
    title: str
    url: str
    summary: str
    published_at: str  # ISO8601 timestamp

class NewsSearchResponse(BaseModel):
    results: List[NewsArticle] 