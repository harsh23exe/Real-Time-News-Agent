import os

class Config:
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_HOST = os.getenv('PINECONE_HOST', '')
    PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', '')
    PINECONE_NAMESPACE = os.getenv('PINECONE_NAMESPACE', '')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    DEPLOYMENT = os.getenv('DEPLOYMENT', 'development')  # 'production', 'development', 'staging'

    @classmethod
    def validate_config(cls):
        if not cls.PINECONE_API_KEY or not cls.PINECONE_HOST or not cls.PINECONE_INDEX_NAME or not cls.PINECONE_NAMESPACE:
            raise ValueError('Missing Pinecone configuration environment variables.')
    
    @classmethod
    def is_production(cls):
        """Check if running in production environment"""
        return cls.DEPLOYMENT.lower() == 'production'
    
    @classmethod
    def should_use_external_services(cls):
        """Determine if external services (Pinecone, file I/O) should be used"""
        # In production, use read-only mode to avoid write operations
        # In development/staging, allow all operations
        return cls.DEPLOYMENT.lower() in ['development', 'staging'] 