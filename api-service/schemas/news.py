from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class NewsSearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 15

class NewsArticle(BaseModel):
    id: str  # Pinecone record ID
    title: str
    url: str
    summary: str
    published_at: str  # ISO8601 timestamp

class NewsSearchResponse(BaseModel):
    results: List[NewsArticle]

class NewsFetchRequest(BaseModel):
    ids: List[str]

class PineconeRecord(BaseModel):
    id: str
    metadata: Optional[Dict[str, Any]] = None

class NewsFetchResponse(BaseModel):
    success: bool
    records: Dict[str, PineconeRecord]
    namespace: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    total_fetched: int
    error: Optional[str] = None 