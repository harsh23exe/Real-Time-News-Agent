import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from services.news_pipeline import NewsPipeline


class TestNewsPipeline(unittest.TestCase):
    """Test cases for the NewsPipeline class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the configuration validation
        with patch('services.news_pipeline.Config') as mock_config:
            mock_config.validate_config.return_value = True
            
            # Mock the services
            with patch('services.news_pipeline.NewsAPIService') as mock_news_service, \
                 patch('services.news_pipeline.PineconeService') as mock_pinecone_service:
                
                self.mock_news_service = Mock()
                self.mock_pinecone_service = Mock()
                mock_news_service.return_value = self.mock_news_service
                mock_pinecone_service.return_value = self.mock_pinecone_service
                
                self.pipeline = NewsPipeline()
    
    def test_init_success(self):
        """Test successful pipeline initialization"""
        with patch('services.news_pipeline.Config') as mock_config, \
             patch('services.news_pipeline.NewsAPIService') as mock_news_service, \
             patch('services.news_pipeline.PineconeService') as mock_pinecone_service:
            
            mock_config.validate_config.return_value = True
            mock_news_service.return_value = Mock()
            mock_pinecone_service.return_value = Mock()
            
            pipeline = NewsPipeline()
            self.assertIsNotNone(pipeline)
    
    def test_init_failure(self):
        """Test pipeline initialization failure"""
        with patch('services.news_pipeline.Config') as mock_config:
            mock_config.validate_config.side_effect = ValueError("Missing API keys")
            
            with self.assertRaises(ValueError):
                NewsPipeline()
    
    def test_prepare_article_text(self):
        """Test article text preparation"""
        article = {
            'title': 'Test Title',
            'description': 'Test Description',
            'content': 'Test Content that is longer than 1000 characters ' * 100
        }
        
        result = self.pipeline._prepare_article_text(article)
        
        self.assertIn('Test Title', result)
        self.assertIn('Test Description', result)
        self.assertIn('Test Content', result)
        # Should be truncated to 1000 characters
        self.assertLess(len(result), 2000)
    
    def test_prepare_article_metadata(self):
        """Test article metadata preparation"""
        article = {
            'title': 'Test Article',
            'description': 'Test Description',
            'url': 'https://example.com',
            'publishedAt': '2024-01-01T00:00:00Z',
            'source': {'name': 'Test Source'},
            'author': 'Test Author',
            'urlToImage': 'https://example.com/image.jpg'
        }
        
        result = self.pipeline._prepare_article_metadata(article, 'test_topic')
        
        self.assertEqual(result['title'], 'Test Article')
        self.assertEqual(result['description'], 'Test Description')
        self.assertEqual(result['url'], 'https://example.com')
        self.assertEqual(result['source_name'], 'Test Source')
        self.assertEqual(result['author'], 'Test Author')
        self.assertEqual(result['source_type'], 'test_topic')
        self.assertEqual(result['content_type'], 'news_article')
        self.assertIn('image_url', result)
    
    def test_process_news_topic_success(self):
        """Test successful news topic processing"""
        # Mock news service response
        mock_articles = [
            {
                'title': 'Article 1',
                'description': 'Description 1',
                'url': 'https://example1.com',
                'publishedAt': '2024-01-01T00:00:00Z',
                'source': {'name': 'Source 1'},
                'author': 'Author 1'
            },
            {
                'title': 'Article 2',
                'description': 'Description 2',
                'url': 'https://example2.com',
                'publishedAt': '2024-01-02T00:00:00Z',
                'source': {'name': 'Source 2'},
                'author': 'Author 2'
            }
        ]
        
        self.mock_news_service.fetch_news.return_value = mock_articles
        
        # Mock pinecone service response
        self.mock_pinecone_service.upsert_text.return_value = {'success': True, 'record_id': 'test_id'}
        
        result = self.pipeline.process_news_topic('artificial intelligence')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['topic'], 'artificial intelligence')
        self.assertEqual(result['articles_fetched'], 2)
        self.assertEqual(result['articles_processed'], 2)
        self.assertEqual(result['articles_failed'], 0)
        self.assertIn('timestamp', result)
    
    def test_process_news_topic_no_articles(self):
        """Test news topic processing with no articles"""
        self.mock_news_service.fetch_news.return_value = []
        
        result = self.pipeline.process_news_topic('nonexistent topic')
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'No articles found')
        self.assertEqual(result['articles_processed'], 0)
    
    def test_process_news_topic_pinecone_failure(self):
        """Test news topic processing with Pinecone failure"""
        mock_articles = [
            {
                'title': 'Article 1',
                'description': 'Description 1',
                'url': 'https://example1.com',
                'publishedAt': '2024-01-01T00:00:00Z',
                'source': {'name': 'Source 1'},
                'author': 'Author 1'
            }
        ]
        
        self.mock_news_service.fetch_news.return_value = mock_articles
        self.mock_pinecone_service.upsert_text.return_value = {'success': False, 'error': 'Pinecone error'}
        
        result = self.pipeline.process_news_topic('test topic')
        
        self.assertTrue(result['success'])  # Pipeline succeeds but with failures
        self.assertEqual(result['articles_fetched'], 1)
        self.assertEqual(result['articles_processed'], 0)
        self.assertEqual(result['articles_failed'], 1)
    
    def test_process_top_headlines_success(self):
        """Test successful top headlines processing"""
        mock_articles = [
            {
                'title': 'Headline 1',
                'description': 'Headline Description 1',
                'url': 'https://headline1.com',
                'publishedAt': '2024-01-01T00:00:00Z',
                'source': {'name': 'Headline Source 1'},
                'author': 'Headline Author 1'
            }
        ]
        
        self.mock_news_service.fetch_top_headlines.return_value = mock_articles
        self.mock_pinecone_service.upsert_text.return_value = {'success': True, 'record_id': 'headline_id'}
        
        result = self.pipeline.process_top_headlines(country='us', category='technology')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['country'], 'us')
        self.assertEqual(result['category'], 'technology')
        self.assertEqual(result['articles_fetched'], 1)
        self.assertEqual(result['articles_processed'], 1)
        self.assertEqual(result['articles_failed'], 0)
    
    def test_process_domain_news_success(self):
        """Test successful domain news processing"""
        mock_articles = [
            {
                'title': 'Domain Article 1',
                'description': 'Domain Description 1',
                'url': 'https://domain1.com',
                'publishedAt': '2024-01-01T00:00:00Z',
                'source': {'name': 'Domain Source 1'},
                'author': 'Domain Author 1'
            }
        ]
        
        self.mock_news_service.fetch_news_by_domain.return_value = mock_articles
        self.mock_pinecone_service.upsert_text.return_value = {'success': True, 'record_id': 'domain_id'}
        
        result = self.pipeline.process_domain_news(domain='example.com')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['domain'], 'example.com')
        self.assertEqual(result['articles_fetched'], 1)
        self.assertEqual(result['articles_processed'], 1)
        self.assertEqual(result['articles_failed'], 0)
    
    def test_batch_process_topics_success(self):
        """Test successful batch topic processing"""
        topics = ['topic1', 'topic2']
        
        # Mock individual topic processing results
        def mock_process_topic(topic, **kwargs):
            return {
                'success': True,
                'topic': topic,
                'articles_fetched': 2,
                'articles_processed': 2,
                'articles_failed': 0
            }
        
        self.pipeline.process_news_topic = mock_process_topic
        
        result = self.pipeline.batch_process_topics(topics)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['topics_processed'], 2)
        self.assertEqual(result['total_articles_processed'], 4)
        self.assertEqual(result['total_articles_failed'], 0)
        self.assertEqual(len(result['individual_results']), 2)
    
    def test_get_pipeline_status_success(self):
        """Test successful pipeline status check"""
        self.mock_news_service.get_api_status.return_value = {'status': 'ok'}
        self.mock_pinecone_service.get_index_stats.return_value = {'success': True, 'stats': {}}
        
        result = self.pipeline.get_pipeline_status()
        
        self.assertTrue(result['success'])
        self.assertIn('news_api_status', result)
        self.assertIn('pinecone_status', result)
        self.assertIn('timestamp', result)
    
    def test_get_pipeline_status_failure(self):
        """Test pipeline status check failure"""
        self.mock_news_service.get_api_status.side_effect = Exception("API Error")
        
        result = self.pipeline.get_pipeline_status()
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_close(self):
        """Test pipeline cleanup"""
        self.pipeline.close()
        
        # Verify pinecone service close was called
        self.mock_pinecone_service.close.assert_called_once()


if __name__ == '__main__':
    unittest.main() 