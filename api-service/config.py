import os

class Config:
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_HOST = os.getenv('PINECONE_HOST', '')
    PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', '')
    PINECONE_NAMESPACE = os.getenv('PINECONE_NAMESPACE', '')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')

    @classmethod
    def validate_config(cls):
        if not cls.PINECONE_API_KEY or not cls.PINECONE_HOST or not cls.PINECONE_INDEX_NAME or not cls.PINECONE_NAMESPACE:
            raise ValueError('Missing Pinecone configuration environment variables.') 