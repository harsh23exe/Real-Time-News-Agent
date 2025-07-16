from typing import List, Dict, Any, Optional
from datetime import datetime
from services.news_api_service import NewsAPIService
from services.pinecone_service import PineconeService
from utils.logger import logger
from config import Config


class NewsPipeline:
    """Pipeline to fetch news from NewsAPI and upload to Pinecone database"""
    
    def __init__(self):
        """Initialize the pipeline with NewsAPI and Pinecone services"""
        try:
            # Validate configuration
            Config.validate_config()
            
            # Initialize services
            self.news_service = NewsAPIService()
            self.pinecone_service = PineconeService()
            
            logger.info("News pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing news pipeline: {e}")
            raise
    
    def process_news_topic(self, topic: str, from_date: Optional[str] = None,
                          language: Optional[str] = None, sort_by: Optional[str] = None) -> Dict[str, Any]:
        """Process news for a specific topic: fetch and upload to database"""
        try:
            logger.info(f"Starting pipeline for topic: {topic}")
            
            # Step 1: Fetch news from NewsAPI
            articles = self.news_service.fetch_news(
                topic=topic,
                from_date=from_date,
                language=language,
                sort_by=sort_by
            )
            
            if not articles:
                logger.warning(f"No articles found for topic: {topic}")
                return {
                    'success': False,
                    'error': 'No articles found',
                    'topic': topic,
                    'articles_processed': 0
                }
            
            # Step 2: Process and upload articles to Pinecone
            processed_count = 0
            failed_count = 0
            
            for article in articles:
                try:
                    # Prepare article text for vectorization
                    article_text = self._prepare_article_text(article)
                    
                    # Prepare metadata
                    metadata = self._prepare_article_metadata(article, topic)
                    
                    # Upload to Pinecone
                    result = self.pinecone_service.upsert_text(
                        text=article_text,
                        metadata=metadata,
                        record_id=f"news_{article.get('publishedAt', '')}_{hash(article.get('url', ''))}"
                    )
                    
                    if result['success']:
                        processed_count += 1
                        logger.debug(f"Successfully processed article: {article.get('title', 'Unknown')}")
                    else:
                        failed_count += 1
                        logger.error(f"Failed to process article: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error processing article: {e}")
            
            logger.info(f"Pipeline completed for topic '{topic}': {processed_count} processed, {failed_count} failed")
            
            return {
                'success': True,
                'topic': topic,
                'articles_fetched': len(articles),
                'articles_processed': processed_count,
                'articles_failed': failed_count,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in news pipeline for topic '{topic}': {e}")
            return {
                'success': False,
                'error': str(e),
                'topic': topic
            }
    
    def process_top_headlines(self, country: str = 'us', category: Optional[str] = None) -> Dict[str, Any]:
        """Process top headlines and upload to database"""
        try:
            logger.info(f"Starting pipeline for top headlines (country: {country}, category: {category})")
            
            # Step 1: Fetch top headlines
            articles = self.news_service.fetch_top_headlines(country=country, category=category)
            
            if not articles:
                logger.warning(f"No top headlines found for country: {country}")
                return {
                    'success': False,
                    'error': 'No headlines found',
                    'country': country,
                    'category': category,
                    'articles_processed': 0
                }
            
            # Step 2: Process and upload articles
            processed_count = 0
            failed_count = 0
            
            for article in articles:
                try:
                    article_text = self._prepare_article_text(article)
                    metadata = self._prepare_article_metadata(article, f"headlines_{country}")
                    
                    result = self.pinecone_service.upsert_text(
                        text=article_text,
                        metadata=metadata,
                        record_id=f"headlines_{article.get('publishedAt', '')}_{hash(article.get('url', ''))}"
                    )
                    
                    if result['success']:
                        processed_count += 1
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error processing headline: {e}")
            
            logger.info(f"Headlines pipeline completed: {processed_count} processed, {failed_count} failed")
            
            return {
                'success': True,
                'country': country,
                'category': category,
                'articles_fetched': len(articles),
                'articles_processed': processed_count,
                'articles_failed': failed_count,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in headlines pipeline: {e}")
            return {
                'success': False,
                'error': str(e),
                'country': country,
                'category': category
            }
    
    def process_domain_news(self, domain: str, from_date: Optional[str] = None) -> Dict[str, Any]:
        """Process news from a specific domain and upload to database"""
        try:
            logger.info(f"Starting pipeline for domain: {domain}")
            
            # Step 1: Fetch news from domain
            articles = self.news_service.fetch_news_by_domain(domain=domain, from_date=from_date)
            
            if not articles:
                logger.warning(f"No articles found for domain: {domain}")
                return {
                    'success': False,
                    'error': 'No articles found',
                    'domain': domain,
                    'articles_processed': 0
                }
            
            # Step 2: Process and upload articles
            processed_count = 0
            failed_count = 0
            
            for article in articles:
                try:
                    article_text = self._prepare_article_text(article)
                    metadata = self._prepare_article_metadata(article, f"domain_{domain}")
                    
                    result = self.pinecone_service.upsert_text(
                        text=article_text,
                        metadata=metadata,
                        record_id=f"domain_{domain}_{article.get('publishedAt', '')}_{hash(article.get('url', ''))}"
                    )
                    
                    if result['success']:
                        processed_count += 1
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error processing domain article: {e}")
            
            logger.info(f"Domain pipeline completed for '{domain}': {processed_count} processed, {failed_count} failed")
            
            return {
                'success': True,
                'domain': domain,
                'articles_fetched': len(articles),
                'articles_processed': processed_count,
                'articles_failed': failed_count,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in domain pipeline for '{domain}': {e}")
            return {
                'success': False,
                'error': str(e),
                'domain': domain
            }
    
    def batch_process_topics(self, topics: List[str], from_date: Optional[str] = None) -> Dict[str, Any]:
        """Process multiple topics in batch"""
        try:
            logger.info(f"Starting batch pipeline for {len(topics)} topics")
            
            results = []
            total_processed = 0
            total_failed = 0
            
            for topic in topics:
                result = self.process_news_topic(topic=topic, from_date=from_date)
                results.append(result)
                
                if result['success']:
                    total_processed += result['articles_processed']
                    total_failed += result['articles_failed']
                else:
                    total_failed += 1
            
            logger.info(f"Batch pipeline completed: {total_processed} total processed, {total_failed} total failed")
            
            return {
                'success': True,
                'topics_processed': len(topics),
                'total_articles_processed': total_processed,
                'total_articles_failed': total_failed,
                'individual_results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in batch pipeline: {e}")
            return {
                'success': False,
                'error': str(e),
                'topics': topics
            }
    
    def _prepare_article_text(self, article: Dict[str, Any]) -> str:
        """Prepare article text for vectorization"""
        title = article.get('title', '')
        description = article.get('description', '')
        content = article.get('content', '')
        
        # Combine title, description, and content
        text_parts = []
        if title:
            text_parts.append(title)
        if description:
            text_parts.append(description)
        if content:
            # Remove content after first 1000 characters to avoid too long texts
            text_parts.append(content[:1000])
        
        return ' '.join(text_parts).strip()
    
    def _prepare_article_metadata(self, article: Dict[str, Any], source_type: str) -> Dict[str, Any]:
        """Prepare metadata for the article"""
        metadata = {
            'source_type': source_type,
            'title': article.get('title', ''),
            'description': article.get('description', ''),
            'url': article.get('url', ''),
            'published_at': article.get('publishedAt', ''),
            'source_name': article.get('source', {}).get('name', ''),
            'author': article.get('author', ''),
            'content_type': 'news_article',
            'processed_at': datetime.now().isoformat()
        }
        
        # Add additional metadata if available
        if article.get('urlToImage'):
            metadata['image_url'] = article.get('urlToImage')
        
        return metadata
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get status of both services"""
        try:
            news_status = self.news_service.get_api_status()
            pinecone_status = self.pinecone_service.get_index_stats()
            
            return {
                'success': True,
                'news_api_status': news_status,
                'pinecone_status': pinecone_status,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting pipeline status: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def close(self):
        """Clean up resources"""
        try:
            self.pinecone_service.close()
            logger.info("News pipeline closed")
        except Exception as e:
            logger.error(f"Error closing news pipeline: {e}") 