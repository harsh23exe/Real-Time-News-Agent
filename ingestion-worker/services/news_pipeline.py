from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from services.news_api_service import NewsAPIService
from services.pinecone_service import PineconeService
from utils.logger import logger
from config import Config


class NewsPipeline:
    """Pipeline to fetch news from NewsAPI and upload to Pinecone database"""
    
    def __init__(self):
        try:
            Config.validate_config()
            self.news_service = NewsAPIService()
            self.pinecone_service = PineconeService()
            logger.info("News pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing news pipeline: {e}")
            raise
    
    def process_news_topic(self, topic: str, language: Optional[str] = None, sort_by: Optional[str] = None) -> Dict[str, Any]:
        """Process news for a specific topic: fetch and upload to database"""
        try:
            logger.info(f"Starting pipeline for topic: {topic}")
            articles = self.news_service.fetch_news(
                topic=topic,
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
            processed_count = 0
            failed_count = 0
            for article in articles:
                try:
                    article_text = self._prepare_article_text(article)
                    metadata = self._prepare_article_metadata(article, topic)
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
        try:
            logger.info(f"Starting pipeline for top headlines (country: {country}, category: {category})")
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
    
    def process_domain_news(self, domain: str) -> Dict[str, Any]:
        try:
            logger.info(f"Starting pipeline for domain: {domain}")
            articles = self.news_service.fetch_news_by_domain(domain=domain)
            if not articles:
                logger.warning(f"No articles found for domain: {domain}")
                return {
                    'success': False,
                    'error': 'No articles found',
                    'domain': domain,
                    'articles_processed': 0
                }
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
    
    def batch_process_topics(self, topics: List[str]) -> Dict[str, Any]:
        try:
            logger.info(f"Starting batch pipeline for {len(topics)} topics")
            
            all_texts = []
            all_metadata = []
            all_record_ids = []
            total_articles_fetched = 0
            total_articles_failed = 0
            
            # Fetch articles for all topics
            for topic in topics:
                try:
                    articles = self.news_service.fetch_news(topic=topic)
                    total_articles_fetched += len(articles)
                    
                    for article in articles:
                        try:
                            article_text = self._prepare_article_text(article)
                            metadata = self._prepare_article_metadata(article, topic)
                            record_id = f"batch_{topic}_{article.get('publishedAt', '')}_{hash(article.get('url', ''))}"
                            
                            all_texts.append(article_text)
                            all_metadata.append(metadata)
                            all_record_ids.append(record_id)
                            
                        except Exception as e:
                            total_articles_failed += 1
                            logger.error(f"Error processing article for topic '{topic}': {e}")
                            
                except Exception as e:
                    logger.error(f"Error fetching articles for topic '{topic}': {e}")
                    total_articles_failed += 1
            
            # Batch upsert all articles to Pinecone
            if all_texts:
                batch_result = self.pinecone_service.upsert_texts_batch(
                    texts=all_texts,
                    metadata_list=all_metadata,
                    record_ids=all_record_ids
                )
                
                if batch_result['success']:
                    total_processed = batch_result.get('successful', 0)
                    total_articles_failed += batch_result.get('failed', 0)
                    logger.info(f"Successfully batch upserted {total_processed} articles")
                else:
                    total_processed = batch_result.get('successful', 0)
                    total_articles_failed += batch_result.get('failed', len(all_texts))
                    logger.error(f"Batch upsert failed: {batch_result.get('error', 'Unknown error')}")
            else:
                total_processed = 0
                logger.warning("No articles found for any topics")
            
            logger.info(f"Batch pipeline completed: {total_processed} total processed, {total_articles_failed} total failed")
            
            return {
                'success': True,
                'topics_processed': len(topics),
                'total_articles_fetched': total_articles_fetched,
                'total_articles_processed': total_processed,
                'total_articles_failed': total_articles_failed,
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
        title = article.get('title', '')
        description = article.get('description', '')
        content = article.get('content', '')
        text_parts = []
        if title:
            text_parts.append(title)
        if description:
            text_parts.append(description)
        if content:
            text_parts.append(content[:1000])
        return ' '.join(text_parts).strip()
    
    def _prepare_article_metadata(self, article: Dict[str, Any], source_type: str) -> Dict[str, Any]:
        # Helper function to safely get string values
        def safe_get_string(value, default=''):
            if value is None or value == '':
                return default
            return str(value)
        
        metadata = {
            'source_type': source_type,
            'title': safe_get_string(article.get('title')),
            'description': safe_get_string(article.get('description')),
            'url': safe_get_string(article.get('url')),
            'published_at': safe_get_string(article.get('publishedAt')),
            'source_name': safe_get_string(article.get('source', {}).get('name')),
            'author': safe_get_string(article.get('author')),
            'content_type': 'news_article',
            'processed_at': datetime.now().isoformat()
        }
        
        # Only add image_url if it's not null or empty
        image_url = article.get('urlToImage')
        if image_url and image_url != '':
            metadata['image_url'] = safe_get_string(image_url)
        
        return metadata
    
    def get_pipeline_status(self) -> Dict[str, Any]:
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
        try:
            self.pinecone_service.close()
            logger.info("News pipeline closed")
        except Exception as e:
            logger.error(f"Error closing news pipeline: {e}") 