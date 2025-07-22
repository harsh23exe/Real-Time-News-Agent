from fastapi import APIRouter, HTTPException
from schemas.news import NewsSearchRequest, NewsSearchResponse, NewsArticle
from services.pinecone_service import PineconeService

news_router = APIRouter()

@news_router.post("/search", response_model=NewsSearchResponse)
def search_news(request: NewsSearchRequest):
    pinecone = PineconeService()
    result = pinecone.search_similar(query_text=request.query, top_k=request.limit)
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))
    articles = []
    for match in result.get('matches', []):
        meta = match.get('metadata', {})
        articles.append(NewsArticle(
            title=meta.get('title', ''),
            url=meta.get('url', ''),
            summary=meta.get('summary', ''),
            published_at=meta.get('published_at', '')
        ))
    return NewsSearchResponse(results=articles) 