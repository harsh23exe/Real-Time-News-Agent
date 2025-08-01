from fastapi import APIRouter, HTTPException
from schemas.news import NewsSearchRequest, NewsSearchResponse, NewsArticle, NewsFetchRequest, NewsFetchResponse, PineconeRecord
from services.pinecone_service import PineconeService
from newsapi import NewsApiClient
from config import Config
from utils.logger import logger
from utils.headlines_cache import HeadlinesCache
from datetime import datetime

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
            id=match.get('id', ''),  # Include Pinecone record ID
            title=meta.get('title', ''),
            url=meta.get('url', ''),
            summary=meta.get('summary', '') or meta.get('description', ''),  # Handle both summary and description
            published_at=meta.get('published_at', '')
        ))
    return NewsSearchResponse(results=articles)

@news_router.post("/fetch", response_model=NewsFetchResponse)
def fetch_records(request: NewsFetchRequest):
    """Fetch records from Pinecone by their IDs"""
    pinecone = PineconeService()
    result = pinecone.fetch_records(record_ids=request.ids)
    
    if not result.get('success'):
        return NewsFetchResponse(
            success=False,
            records={},
            total_fetched=0,
            error=result.get('error', 'Unknown error')
        )
    
    # Convert the raw Pinecone records to our schema format
    formatted_records = {}
    raw_records = result.get('records', {})
    
    for record_id, record_data in raw_records.items():
        formatted_records[record_id] = PineconeRecord(
            id=record_data.id,
            metadata=record_data.metadata or {}
        )
    
    return NewsFetchResponse(
        success=True,
        records=formatted_records,
        namespace=result.get('namespace'),
        usage=result.get('usage'),
        total_fetched=result.get('total_fetched', 0)
    )

@news_router.get("/headlines", response_model=NewsSearchResponse)
def get_top_headlines(country: str = 'us', category: str = 'technology', limit: int = 20):
    cache = HeadlinesCache()
    
    # Clear old cache files
    cache.clear_old_cache()
    
    # Check if we have cached headlines for today
    cached_headlines = cache.get_cached_headlines(country, category)
    
    if cached_headlines:
        # Convert cached headlines to NewsArticle format
        news_articles = []
        for headline in cached_headlines[:limit]:
            news_articles.append(NewsArticle(
                id=headline.get('id', ''),
                title=headline.get('title', ''),
                url=headline.get('url', ''),
                summary=headline.get('summary', ''),
                published_at=headline.get('published_at', '')
            ))
        logger.info(f"Returned {len(news_articles)} headlines from cache")
        return NewsSearchResponse(results=news_articles)
    
    # If no cache, fetch from NewsAPI
    client = NewsApiClient(api_key=Config.NEWS_API_KEY)
    pinecone = PineconeService()
    
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
            logger.info(f"Fetched {len(article_list)} top headlines from NewsAPI for country: {country}")
            
            news_articles = []
            headlines_for_cache = []
            pinecone_records = []  # Batch records for Pinecone
            
            for article in article_list[:20]:  # Limit to 20 headlines max
                # Generate ID similar to the ingestion pipeline
                published_at = article.get('publishedAt') or datetime.now().isoformat()
                url = article.get('url') or ''
                record_id = f"headlines_{published_at}_{hash(url)}"
                
                # Prepare article data
                article_data = {
                    'id': record_id,
                    'title': article.get('title') or '',
                    'url': url,
                    'summary': article.get('description') or '',
                    'published_at': published_at
                }
                
                news_articles.append(NewsArticle(**article_data))
                headlines_for_cache.append(article_data)
                
                # Prepare record for batch Pinecone storage
                if Config.should_use_external_services():
                    article_text = f"{article.get('title', '')} {article.get('description', '')}"
                    metadata = {
                        'source_type': f"headlines_{country}",
                        'title': article.get('title') or '',
                        'summary': article.get('description') or '',
                        'url': url,
                        'published_at': published_at,
                        'source_name': article.get('source', {}).get('name', ''),
                        'author': article.get('author') or '',
                        'content_type': 'news_headline',
                        'processed_at': datetime.now().isoformat(),
                        'country': country
                    }
                    
                    if category:
                        metadata['category'] = category
                    
                    pinecone_records.append({
                        'id': record_id,
                        'text': article_text.strip(),
                        'metadata': metadata
                    })
            
            # Batch store in Pinecone (single API call instead of 20)
            if pinecone_records and Config.should_use_external_services():
                try:
                    result = pinecone.upsert_batch(pinecone_records)
                    if result.get('success'):
                        logger.info(f"Successfully batch stored {result.get('count', 0)} headlines in Pinecone")
                    else:
                        logger.error(f"Failed to batch store headlines in Pinecone: {result.get('error')}")
                except Exception as e:
                    logger.error(f"Error batch storing headlines in Pinecone: {e}")
            elif not Config.should_use_external_services():
                logger.info(f"Skipping Pinecone storage in production environment (DEPLOYMENT={Config.DEPLOYMENT})")
            
            # Cache the headlines
            cache.save_headlines(headlines_for_cache, country, category)
            
            return NewsSearchResponse(results=news_articles[:limit])
        else:
            logger.error(f"NewsAPI error: {articles.get('message', 'Unknown error')}")
            return NewsSearchResponse(results=[])
            
    except Exception as e:
        logger.error(f"Error fetching top headlines: {e}")
        return NewsSearchResponse(results=[])