import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class to manage all environment variables and settings"""
    
    # API Keys
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    
 
    NEWS_LANGUAGE = 'en'
    NEWS_FROM_DATE = '2025-07-14'
    NEWS_SORT_BY = 'publishedAt'
    
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        required_vars = [
            'NEWS_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True 