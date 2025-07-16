from pinecone import Pinecone
from typing import List, Dict, Any, Optional
import uuid
from config import Config
from utils.logger import logger


class PineconeService:
    """Service class to handle Pinecone vector database operations using native text embedding"""
    
    def __init__(self):
        """Initialize Pinecone client"""
        try:
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
            
            # Get index
            self.index = self.pc.Index(host=Config.PINECONE_HOST)
            self.namespace = Config.PINECONE_NAMESPACE
            
            logger.info(f"Pinecone service initialized with index host: {Config.PINECONE_HOST}")
            
        except Exception as e:
            logger.error(f"Error initializing Pinecone service: {e}")
            raise
    
    def upsert_text(self, text: str, metadata: Optional[Dict[str, Any]] = None, 
                   record_id: Optional[str] = None) -> Dict[str, Any]:
        """Upsert a single text with its embedding to Pinecone"""
        try:
            # Generate record ID if not provided
            if record_id is None:
                record_id = str(uuid.uuid4())
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            # Add text length
            metadata['text_length'] = len(text)
            
            # Prepare record
            record = {
                "_id": record_id,
                "text": text,
                **metadata
            }
            
            # Upsert to Pinecone
            self.index.upsert_records(
                namespace=self.namespace,
                records=[record]
            )
            
            logger.info(f"Successfully upserted text with ID: {record_id}")
            
            return {
                'success': True,
                'record_id': record_id,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error upserting text: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def upsert_texts_batch(self, texts: List[str], metadata_list: Optional[List[Dict[str, Any]]] = None,
                          record_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Upsert multiple texts in batch"""
        try:
            if not texts:
                return {'success': False, 'error': 'No texts provided'}
            
            # Prepare records
            records = []
            for i, text in enumerate(texts):
                # Generate record ID if not provided
                record_id = record_ids[i] if record_ids and i < len(record_ids) else str(uuid.uuid4())
                
                # Prepare metadata
                metadata = metadata_list[i] if metadata_list and i < len(metadata_list) else {}
                metadata['text_length'] = len(text)
                
                record = {
                    "_id": record_id,
                    "text": text,
                    **metadata
                }
                records.append(record)
            
            # Upsert batch to Pinecone
            self.index.upsert_records(
                namespace=self.namespace,
                records=records
            )
            
            logger.info(f"Successfully upserted {len(texts)} texts in batch")
            
            return {
                'success': True,
                'total_texts': len(texts)
            }
            
        except Exception as e:
            logger.error(f"Error upserting texts batch: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_similar(self, query_text: str, top_k: int = 10, 
                      filter_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search for similar texts using query text"""
        try:
            # Prepare search payload
            search_payload = {
                'inputs': {'text': query_text},
                'top_k': top_k
            }
            if filter_metadata:
                search_payload['filter'] = filter_metadata

            # Use the correct Pinecone search method
            search_results = self.index.search(self.namespace, search_payload)

            # Parse hits from the result
            hits = search_results.get('result', {}).get('hits', [])
            matches = []
            for hit in hits:
                match = {
                    'id': hit.get('_id'),
                    'score': hit.get('_score'),
                    'metadata': hit.get('fields', {})
                }
                matches.append(match)

            logger.info(f"Found {len(matches)} similar texts")

            return {
                'success': True,
                'query': query_text,
                'matches': matches,
                'total_matches': len(matches)
            }

        except Exception as e:
            logger.error(f"Error searching similar texts: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_record(self, record_id: str) -> Dict[str, Any]:
        """Delete a specific record by ID"""
        try:
            result = self.index.delete(
                ids=[record_id],
                namespace=self.namespace
            )
            
            logger.info(f"Successfully deleted record with ID: {record_id}")
            
            return {
                'success': True,
                'deleted_count': result.get('deleted_count', 0)
            }
            
        except Exception as e:
            logger.error(f"Error deleting record: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the Pinecone index"""
        try:
            stats = self.index.describe_index_stats()
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def fetch_records(self, record_ids: List[str]) -> Dict[str, Any]:
        """Fetch specific records by their IDs"""
        try:
            records = self.index.fetch(
                ids=record_ids,
                namespace=self.namespace
            )
            
            return {
                'success': True,
                'records': records.get('vectors', {}),
                'total_fetched': len(records.get('vectors', {}))
            }
            
        except Exception as e:
            logger.error(f"Error fetching records: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def close(self):
        """Clean up resources"""
        try:
            # Pinecone client doesn't require explicit cleanup
            logger.info("Pinecone service closed")
        except Exception as e:
            logger.error(f"Error closing Pinecone service: {e}") 