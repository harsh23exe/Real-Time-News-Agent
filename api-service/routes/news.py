from fastapi import APIRouter, HTTPException
from schemas.news import NewsSearchRequest, NewsSearchResponse, NewsArticle
from services.pinecone_service import PineconeService
from newsapi import NewsApiClient
from config import Config
from utils.logger import logger

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

@news_router.get("/headlines", response_model=NewsSearchResponse)
def get_top_headlines(country: str = 'us', category: str = None, limit: int = 10):
    client = NewsApiClient(api_key=Config.NEWS_API_KEY)
    try:
        if category:
            articles = client.get_top_headlines(
                country=country,
                category=category
            )
        else:
            articles = client.get_top_headlines(country=country)
        
        if articles.get('status') == 'ok':
            article_list = articles.get('articles', [])
            logger.info(f"Fetched {len(article_list)} top headlines for country: {country}")
            news_articles = []
            for article in article_list[:limit]:
                news_articles.append(NewsArticle(
                    title=article.get('title') or '',
                    url=article.get('url') or '',
                    summary=article.get('description') or '',
                    published_at=article.get('publishedAt') or ''
                ))
            return NewsSearchResponse(results=news_articles)
        else:
            logger.error(f"NewsAPI error: {articles.get('message', 'Unknown error')}")
            return NewsSearchResponse(results=[])
            
    except Exception as e:
        logger.error(f"Error fetching top headlines: {e}")
        return NewsSearchResponse(results=[])