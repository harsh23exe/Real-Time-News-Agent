import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class to manage all environment variables and settings"""
    
    # API Keys
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    
    # Pinecone Configuration
    PINECONE_HOST = os.getenv('PINECONE_HOST', '')
    PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', '')
    PINECONE_NAMESPACE = os.getenv('PINECONE_NAMESPACE', '')
    
    # News API Configuration
    NEWS_LANGUAGE = 'en'
    NEWS_FROM_DATE = datetime.now().strftime('%Y-%m-%d')
    NEWS_SORT_BY = 'publishedAt'
    
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        required_vars = [
            'NEWS_API_KEY',
            'PINECONE_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True 