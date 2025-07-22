from pinecone import Pinecone
from typing import List, Dict, Any, Optional
from config import Config
from utils.logger import logger

class PineconeService:
    def __init__(self):
        try:
            self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
            self.index = self.pc.Index(host=Config.PINECONE_HOST)
            self.namespace = Config.PINECONE_NAMESPACE
            logger.info(f"Pinecone service initialized with index host: {Config.PINECONE_HOST}")
        except Exception as e:
            logger.error(f"Error initializing Pinecone service: {e}")
            raise

    def search_similar(self, query_text: str, top_k: int = 10, filter_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            search_payload = {
                'inputs': {'text': query_text},
                'top_k': top_k
            }
            if filter_metadata:
                search_payload['filter'] = filter_metadata
            search_results = self.index.search(self.namespace, search_payload)
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