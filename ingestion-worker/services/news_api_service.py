from newsapi import NewsApiClient
from typing import List, Dict, Any, Optional
from config import Config
from utils.logger import logger

class NewsAPIService:
    """Service class to handle News API operations using the newsapi-python library"""
    
    def __init__(self):
        self.client = NewsApiClient(api_key=Config.NEWS_API_KEY)
    
    def fetch_news(self, topic: str, language: Optional[str] = None, sort_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch news articles for a given topic from NewsAPI"""
        try:
            articles = self.client.get_everything(
                q=topic,
                language=language or Config.NEWS_LANGUAGE,
                sort_by=sort_by or Config.NEWS_SORT_BY
            )
            if articles.get('status') == 'ok':
                article_list = articles.get('articles', [])
                logger.info(f"Fetched {len(article_list)} articles for topic: {topic}")
                return article_list
            else:
                logger.error(f"NewsAPI error: {articles.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []
    
    def fetch_news_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Fetch news articles from a specific domain"""
        try:
            articles = self.client.get_everything(
                domains=domain,
                language=Config.NEWS_LANGUAGE,
                sort_by=Config.NEWS_SORT_BY
            )
            
            if articles.get('status') == 'ok':
                article_list = articles.get('articles', [])
                logger.info(f"Fetched {len(article_list)} articles from domain: {domain}")
                return article_list
            else:
                logger.error(f"NewsAPI error: {articles.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching news from domain: {e}")
            return []
    
    def fetch_top_headlines(self, country: str = 'us', category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch top headlines from NewsAPI"""
        try:
            if category:
                articles = self.client.get_top_headlines(
                    country=country,
                    category=category
                )
            else:
                articles = self.client.get_top_headlines(country=country)
            
            if articles.get('status') == 'ok':
                article_list = articles.get('articles', [])
                logger.info(f"Fetched {len(article_list)} top headlines for country: {country}")
                return article_list
            else:
                logger.error(f"NewsAPI error: {articles.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching top headlines: {e}")
            return []
    
    def search_articles(self, query: str, to_date: Optional[str] = None, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for articles with specific criteria"""
        try:
            articles = self.client.get_everything(
                q=query,
                language=language or Config.NEWS_LANGUAGE,
                to=to_date,
                sort_by=Config.NEWS_SORT_BY
            )
            
            if articles.get('status') == 'ok':
                article_list = articles.get('articles', [])
                logger.info(f"Found {len(article_list)} articles for query: {query}")
                return article_list
            else:
                logger.error(f"NewsAPI error: {articles.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            return []
    
    def get_api_status(self) -> Dict[str, Any]:
        """Check News API status and quota"""
        try:
            # Make a simple request to check API status
            articles = self.client.get_everything(q='test')
            
            if articles.get('status') == 'ok':
                return {
                    'status': 'ok',
                    'total_results': articles.get('totalResults', 0),
                    'articles_found': len(articles.get('articles', []))
                }
            else:
                return {
                    'status': 'error',
                    'message': articles.get('message', 'Unknown error')
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            } 