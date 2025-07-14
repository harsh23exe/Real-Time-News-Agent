import unittest
from unittest.mock import patch, Mock
from services.news_api_service import NewsAPIService

class TestNewsAPIService(unittest.TestCase):
    """Test cases for NewsAPIService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.news_service = NewsAPIService()
        
    
    @patch('services.news_api_service.NewsApiClient')
    def test_fetch_news_api_error(self, mock_client_class):
        """Test news fetching with API error"""
        # Mock API error response
        mock_client = Mock()
        mock_client.get_everything.return_value = {
            'status': 'error',
            'message': 'API key invalid'
        }
        mock_client_class.return_value = mock_client
        
        # Test the method
        articles = self.news_service.fetch_news('AI')
        
        # Assertions
        self.assertEqual(len(articles), 0)
    
    @patch('services.news_api_service.NewsApiClient')
    def test_fetch_news_exception(self, mock_client_class):
        """Test news fetching with exception"""
        # Mock exception
        mock_client = Mock()
        mock_client.get_everything.side_effect = Exception("Network error")
        mock_client_class.return_value = mock_client
        
        # Test the method
        articles = self.news_service.fetch_news('AI')
        
        # Assertions
        self.assertEqual(len(articles), 0)
    
    
    def test_fetch_top_headlines(self):
        """Test fetching top headlines"""
        
        articles = self.news_service.fetch_top_headlines('us')
        
        # Assertions
        self.assertEqual(len(articles)>0, True)


    

    def test_fetch_top_headlines_with_category(self):
        """Test fetching top headlines with category"""
        
        # Test the method
        articles = self.news_service.fetch_top_headlines('us', 'technology')
        
        # Assertions
        self.assertEqual(len(articles)>0, True)
        
    def test_get_api_status_success(self):
        """Test API status check success"""
        
        # Test the method
        status = self.news_service.get_api_status()
        
        # Assertions
        self.assertEqual(status['status'], 'ok')


if __name__ == '__main__':
    unittest.main() 