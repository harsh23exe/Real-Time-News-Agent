import unittest
from unittest.mock import Mock, patch
from services.pinecone_service import PineconeService
from config import Config


class TestPineconeService(unittest.TestCase):
    """Test cases for PineconeService"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_pinecone_patcher = patch('services.pinecone_service.Pinecone')
        self.mock_pinecone = self.mock_pinecone_patcher.start()
        
        # Mock Pinecone client and index
        self.mock_pc = Mock()
        self.mock_index = Mock()
        self.mock_pinecone.return_value = self.mock_pc
        self.mock_pc.Index.return_value = self.mock_index
        
        # Mock upsert response (returns None on success)
        self.mock_index.upsert_records.return_value = None
        
        # Mock search response (updated to match new Pinecone search structure)
        self.mock_index.search.return_value = {
            'result': {
                'hits': [
                    {'_id': 'test1', '_score': 0.95, 'fields': {'category': 'test', 'text': 'foo'}},
                    {'_id': 'test2', '_score': 0.85, 'fields': {'category': 'test', 'text': 'bar'}}
                ]
            }
        }
        
        # Mock delete response
        self.mock_index.delete.return_value = {'deleted_count': 1}
        
        # Mock stats response
        self.mock_index.describe_index_stats.return_value = {
            'total_vector_count': 100,
            'dimension': 512,
            'metric': 'cosine'
        }
        
        # Mock fetch response
        self.mock_index.fetch.return_value = {
            'vectors': {
                'test1': {'id': 'test1', 'metadata': {'category': 'test', 'text': 'foo'}},
                'test2': {'id': 'test2', 'metadata': {'category': 'test', 'text': 'bar'}}
            }
        }
        
        self.pinecone_service = PineconeService()
    
    def tearDown(self):
        """Clean up after tests"""
        self.mock_pinecone_patcher.stop()
    
    def test_upsert_text_success(self):
        """Test successful text upsert"""
        text = "This is a test article about artificial intelligence."
        metadata = {"source": "test", "category": "technology"}
        
        result = self.pinecone_service.upsert_text(text, metadata)
        
        self.assertTrue(result['success'])
        self.assertIn('record_id', result)
        self.assertEqual(result['metadata']['source'], 'test')
        self.assertEqual(result['metadata']['category'], 'technology')
    
    def test_upsert_texts_batch_success(self):
        """Test successful batch text upsert"""
        texts = [
            "First article about AI",
            "Second article about machine learning",
            "Third article about deep learning"
        ]
        
        result = self.pinecone_service.upsert_texts_batch(texts)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_texts'], 3)
    
    def test_search_similar(self):
        """Test searching for similar texts"""
        query = "artificial intelligence"
        
        result = self.pinecone_service.search_similar(query, top_k=5)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['query'], query)
        self.assertIn('matches', result)
        self.assertEqual(len(result['matches']), 2)
        # Check that the returned matches have 'text' in metadata
        for match in result['matches']:
            self.assertIn('text', match['metadata'])
    
    def test_delete_record(self):
        """Test deleting a record"""
        record_id = "test-record-id"
        
        result = self.pinecone_service.delete_record(record_id)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['deleted_count'], 1)
    
    def test_get_index_stats(self):
        """Test getting index statistics"""
        result = self.pinecone_service.get_index_stats()
        
        self.assertTrue(result['success'])
        self.assertIn('stats', result)
        self.assertEqual(result['stats']['total_vector_count'], 100)
    
    def test_fetch_records(self):
        """Test fetching specific records"""
        record_ids = ["test1", "test2"]
        
        result = self.pinecone_service.fetch_records(record_ids)
        
        self.assertTrue(result['success'])
        self.assertIn('records', result)
        self.assertEqual(result['total_fetched'], 2)
        # Check that the returned records have 'text' in metadata
        for rec in result['records'].values():
            self.assertIn('text', rec['metadata'])
    
    def test_upsert_text_with_custom_id(self):
        """Test upserting text with custom record ID"""
        text = "Custom ID test"
        custom_id = "custom-test-id"
        
        result = self.pinecone_service.upsert_text(text, record_id=custom_id)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['record_id'], custom_id)
    
    def test_upsert_texts_batch_with_metadata(self):
        """Test batch upsert with metadata"""
        texts = ["Text 1", "Text 2"]
        metadata_list = [
            {"category": "tech", "source": "blog"},
            {"category": "science", "source": "journal"}
        ]
        
        result = self.pinecone_service.upsert_texts_batch(texts, metadata_list)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['total_texts'], 2)
    
    def test_upsert_texts_batch_empty_list(self):
        """Test batch upsert with empty text list"""
        result = self.pinecone_service.upsert_texts_batch([])
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'No texts provided')


if __name__ == '__main__':
    unittest.main() 