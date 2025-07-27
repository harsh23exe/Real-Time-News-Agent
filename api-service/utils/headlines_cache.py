import json
import os
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from pathlib import Path
from utils.logger import logger

class HeadlinesCache:
    """Manages caching of daily headlines to avoid repeated NewsAPI calls"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "headlines_cache.json"
    
    def get_cache_filename(self, country: str, category: Optional[str] = None) -> str:
        """Generate cache filename based on country and category"""
        today = date.today().isoformat()
        if category:
            return f"headlines_{country}_{category}_{today}.json"
        return f"headlines_{country}_{today}.json"
    
    def is_cache_valid(self, country: str, category: Optional[str] = None) -> bool:
        """Check if cached headlines exist for today"""
        cache_file = self.cache_dir / self.get_cache_filename(country, category)
        if not cache_file.exists():
            return False
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is from today
            cache_date = cache_data.get('date', '')
            return cache_date == date.today().isoformat()
        
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error reading cache file: {e}")
            return False
    
    def get_cached_headlines(self, country: str, category: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """Get cached headlines if available and valid"""
        if not self.is_cache_valid(country, category):
            return None
        
        cache_file = self.cache_dir / self.get_cache_filename(country, category)
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            logger.info(f"Retrieved {len(cache_data.get('headlines', []))} headlines from cache")
            return cache_data.get('headlines', [])
        
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error reading cached headlines: {e}")
            return None
    
    def save_headlines(self, headlines: List[Dict[str, Any]], country: str, category: Optional[str] = None) -> bool:
        """Save headlines to cache with today's date"""
        cache_file = self.cache_dir / self.get_cache_filename(country, category)
        
        cache_data = {
            'date': date.today().isoformat(),
            'timestamp': datetime.now().isoformat(),
            'country': country,
            'category': category,
            'headlines': headlines
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"Cached {len(headlines)} headlines for {country}" + 
                       (f"/{category}" if category else ""))
            return True
        
        except Exception as e:
            logger.error(f"Error saving headlines to cache: {e}")
            return False
    
    def clear_old_cache(self):
        """Remove cache files older than today"""
        today = date.today().isoformat()
        
        try:
            for cache_file in self.cache_dir.glob("headlines_*.json"):
                if today not in cache_file.name:
                    cache_file.unlink()
                    logger.info(f"Removed old cache file: {cache_file.name}")
        
        except Exception as e:
            logger.error(f"Error clearing old cache: {e}") 