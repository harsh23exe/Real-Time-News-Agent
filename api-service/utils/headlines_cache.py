import json
import os
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from pathlib import Path
from utils.logger import logger
from config import Config

class HeadlinesCache:
    """Manages caching of daily headlines to avoid repeated NewsAPI calls"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_file = self.cache_dir / "headlines_cache.json"
        
        # Check deployment environment and write permissions
        can_write_files = Config.should_use_external_services()
        
        if can_write_files:
            # Try to create cache directory and test write permissions
            try:
                self.cache_dir.mkdir(exist_ok=True)
                
                # Test if we can actually write to the directory
                test_file = self.cache_dir / "test_write.tmp"
                try:
                    with open(test_file, 'w') as f:
                        f.write("test")
                    test_file.unlink()  # Clean up test file
                    self.use_file_cache = True
                    logger.info(f"Using file-based cache (DEPLOYMENT={Config.DEPLOYMENT})")
                except (OSError, PermissionError):
                    self.use_file_cache = False
                    self.memory_cache = {}
                    logger.info(f"File write failed, using in-memory cache (DEPLOYMENT={Config.DEPLOYMENT})")
                    
            except (OSError, PermissionError):
                self.use_file_cache = False
                self.memory_cache = {}
                logger.info(f"Cache directory creation failed, using in-memory cache (DEPLOYMENT={Config.DEPLOYMENT})")
        else:
            # Production environment - use in-memory cache only
            self.use_file_cache = False
            self.memory_cache = {}
            logger.info(f"Using in-memory cache (production mode, DEPLOYMENT={Config.DEPLOYMENT})")
    
    def get_cache_filename(self, country: str, category: Optional[str] = None) -> str:
        """Generate cache filename based on country and category"""
        today = date.today().isoformat()
        if category:
            return f"headlines_{country}_{category}_{today}.json"
        return f"headlines_{country}_{today}.json"
    
    def get_cache_key(self, country: str, category: Optional[str] = None) -> str:
        """Generate cache key for in-memory storage"""
        today = date.today().isoformat()
        if category:
            return f"{country}_{category}_{today}"
        return f"{country}_{today}"
    
    def is_cache_valid(self, country: str, category: Optional[str] = None) -> bool:
        """Check if cached headlines exist for today"""
        if not self.use_file_cache:
            # Check in-memory cache
            cache_key = self.get_cache_key(country, category)
            return cache_key in self.memory_cache
        
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
        
        if not self.use_file_cache:
            # Get from in-memory cache
            cache_key = self.get_cache_key(country, category)
            cache_data = self.memory_cache.get(cache_key, {})
            headlines = cache_data.get('headlines', [])
            logger.info(f"Retrieved {len(headlines)} headlines from memory cache")
            return headlines
        
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
        cache_data = {
            'date': date.today().isoformat(),
            'timestamp': datetime.now().isoformat(),
            'country': country,
            'category': category,
            'headlines': headlines
        }
        
        if not self.use_file_cache:
            # Save to in-memory cache
            cache_key = self.get_cache_key(country, category)
            self.memory_cache[cache_key] = cache_data
            logger.info(f"Cached {len(headlines)} headlines in memory for {country}" + 
                       (f"/{category}" if category else ""))
            return True
        
        cache_file = self.cache_dir / self.get_cache_filename(country, category)
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"Cached {len(headlines)} headlines for {country}" + 
                       (f"/{category}" if category else ""))
            return True
        
        except Exception as e:
            logger.error(f"Error saving headlines to cache: {e}")
            # If file write fails, fall back to in-memory cache
            self.use_file_cache = False
            self.memory_cache = {}
            cache_key = self.get_cache_key(country, category)
            self.memory_cache[cache_key] = cache_data
            logger.info(f"Fell back to in-memory cache for {country}" + 
                       (f"/{category}" if category else ""))
            return True
    
    def clear_old_cache(self):
        """Remove cache files older than today"""
        if not self.use_file_cache:
            # Clear old in-memory cache entries
            today = date.today().isoformat()
            keys_to_remove = []
            
            for key in self.memory_cache.keys():
                if today not in key:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.memory_cache[key]
                logger.info(f"Removed old memory cache entry: {key}")
            return
        
        today = date.today().isoformat()
        
        try:
            for cache_file in self.cache_dir.glob("headlines_*.json"):
                if today not in cache_file.name:
                    cache_file.unlink()
                    logger.info(f"Removed old cache file: {cache_file.name}")
        
        except Exception as e:
            logger.error(f"Error clearing old cache: {e}") 