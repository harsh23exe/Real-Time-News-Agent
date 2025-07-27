from pinecone import Pinecone
from typing import List, Dict, Any, Optional
from config import Config
from utils.logger import logger
from dotenv import load_dotenv
import os
from pathlib import Path
import uuid

# Always load .env from the project root
env_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=env_path)

class PineconeService:
    def __init__(self):
        try:
            self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
            self.index = self.pc.Index(Config.PINECONE_INDEX_NAME)
            self.namespace = Config.PINECONE_NAMESPACE
            logger.info(f"Pinecone service initialized with index: {Config.PINECONE_INDEX_NAME}")
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

    def fetch_records(self, record_ids: List[str]) -> Dict[str, Any]:
        """Fetch specific records by their IDs"""
        try:
            response = self.index.fetch(
                ids=record_ids,
                namespace=self.namespace
            )
            
            logger.info(f"Successfully fetched {len(response.vectors)} records")
            
            # Convert usage object to dictionary if it exists
            usage_dict = None
            if hasattr(response, 'usage') and response.usage:
                usage_dict = {
                    'read_units': getattr(response.usage, 'read_units', 0)
                }
            
            return {
                'success': True,
                'records': response.vectors,
                'namespace': response.namespace,
                'usage': usage_dict,
                'total_fetched': len(response.vectors)
            }
            
        except Exception as e:
            logger.error(f"Error fetching records: {e}")
            return {
                'success': False,
                'error': str(e)
            } 