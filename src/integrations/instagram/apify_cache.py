"""
Apify Results Cache System
Stores Apify API results locally to minimize API calls and costs
"""

import json
import os
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib
import logging

logger = logging.getLogger(__name__)

class ApifyCache:
    """
    Local cache system for Apify Instagram scraper results
    Stores results with timestamps and handles cache expiration
    """
    
    def __init__(self, cache_dir: str = "cache/apify", default_ttl: int = 3600):
        """
        Initialize cache system
        
        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default time-to-live in seconds (1 hour default)
        """
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create subdirectories for different types of data
        os.makedirs(os.path.join(cache_dir, "user_posts"), exist_ok=True)
        os.makedirs(os.path.join(cache_dir, "profiles"), exist_ok=True)
        os.makedirs(os.path.join(cache_dir, "post_urls"), exist_ok=True)
        
        logger.info(f"ApifyCache initialized with directory: {cache_dir}")
    
    def _generate_cache_key(self, operation: str, params: Dict) -> str:
        """Generate a unique cache key for the operation and parameters"""
        # Create a string representation of the operation and params
        key_data = f"{operation}:{json.dumps(params, sort_keys=True)}"
        
        # Generate MD5 hash for consistent key length
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_file_path(self, operation: str, cache_key: str) -> str:
        """Get the full path for a cache file"""
        if operation == "user_posts":
            return os.path.join(self.cache_dir, "user_posts", f"{cache_key}.json")
        elif operation == "profile":
            return os.path.join(self.cache_dir, "profiles", f"{cache_key}.json")
        elif operation == "post_urls":
            return os.path.join(self.cache_dir, "post_urls", f"{cache_key}.json")
        else:
            return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, operation: str, params: Dict, ttl: Optional[int] = None) -> Optional[Any]:
        """
        Get cached result if available and not expired
        
        Args:
            operation: Type of operation (user_posts, profile, post_urls)
            params: Parameters used for the operation
            ttl: Time-to-live override (uses default if None)
            
        Returns:
            Cached data if available and valid, None otherwise
        """
        cache_key = self._generate_cache_key(operation, params)
        cache_file = self._get_cache_file_path(operation, cache_key)
        
        if not os.path.exists(cache_file):
            logger.debug(f"Cache miss: {cache_key} (file not found)")
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            cached_time = cache_data.get('timestamp', 0)
            current_time = time.time()
            cache_ttl = ttl or self.default_ttl
            
            if current_time - cached_time > cache_ttl:
                logger.debug(f"Cache expired: {cache_key} (age: {current_time - cached_time}s)")
                # Optionally remove expired cache file
                os.remove(cache_file)
                return None
            
            logger.info(f"Cache hit: {cache_key} (age: {current_time - cached_time}s)")
            return cache_data.get('data')
            
        except (json.JSONDecodeError, KeyError, OSError) as e:
            logger.error(f"Error reading cache file {cache_key}: {e}")
            # Remove corrupted cache file
            try:
                os.remove(cache_file)
            except:
                pass
            return None
    
    def set(self, operation: str, params: Dict, data: Any, ttl: Optional[int] = None) -> bool:
        """
        Store data in cache
        
        Args:
            operation: Type of operation (user_posts, profile, post_urls)
            params: Parameters used for the operation
            data: Data to cache
            ttl: Time-to-live override (uses default if None)
            
        Returns:
            True if successfully cached, False otherwise
        """
        cache_key = self._generate_cache_key(operation, params)
        cache_file = self._get_cache_file_path(operation, cache_key)
        
        cache_data = {
            'timestamp': time.time(),
            'operation': operation,
            'params': params,
            'ttl': ttl or self.default_ttl,
            'data': data
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Cached result: {cache_key} ({len(str(data))} chars)")
            return True
            
        except (OSError, TypeError) as e:
            logger.error(f"Error writing cache file {cache_key}: {e}")
            return False
    
    def invalidate(self, operation: str, params: Dict) -> bool:
        """
        Remove specific cached result
        
        Args:
            operation: Type of operation
            params: Parameters used for the operation
            
        Returns:
            True if cache was removed, False if not found
        """
        cache_key = self._generate_cache_key(operation, params)
        cache_file = self._get_cache_file_path(operation, cache_key)
        
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                logger.info(f"Invalidated cache: {cache_key}")
                return True
            except OSError as e:
                logger.error(f"Error removing cache file {cache_key}: {e}")
                return False
        
        return False
    
    def clear_expired(self) -> int:
        """
        Remove all expired cache files
        
        Returns:
            Number of files removed
        """
        removed_count = 0
        current_time = time.time()
        
        for root, dirs, files in os.walk(self.cache_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)
                        
                        cached_time = cache_data.get('timestamp', 0)
                        ttl = cache_data.get('ttl', self.default_ttl)
                        
                        if current_time - cached_time > ttl:
                            os.remove(file_path)
                            removed_count += 1
                            logger.debug(f"Removed expired cache: {file}")
                            
                    except (json.JSONDecodeError, KeyError, OSError):
                        # Remove corrupted files
                        try:
                            os.remove(file_path)
                            removed_count += 1
                        except:
                            pass
        
        if removed_count > 0:
            logger.info(f"Cleared {removed_count} expired cache files")
        
        return removed_count
    
    def clear_all(self) -> int:
        """
        Remove all cache files
        
        Returns:
            Number of files removed
        """
        removed_count = 0
        
        for root, dirs, files in os.walk(self.cache_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        removed_count += 1
                    except OSError:
                        pass
        
        logger.info(f"Cleared all cache: {removed_count} files removed")
        return removed_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        stats = {
            'total_files': 0,
            'total_size_bytes': 0,
            'by_operation': {},
            'oldest_entry': None,
            'newest_entry': None
        }
        
        current_time = time.time()
        oldest_time = float('inf')
        newest_time = 0
        
        for root, dirs, files in os.walk(self.cache_dir):
            operation = os.path.basename(root)
            if operation == 'apify':  # Skip root directory
                continue
                
            operation_stats = {
                'files': 0,
                'size_bytes': 0,
                'expired': 0
            }
            
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        stats['total_files'] += 1
                        stats['total_size_bytes'] += file_size
                        operation_stats['files'] += 1
                        operation_stats['size_bytes'] += file_size
                        
                        # Check if expired
                        with open(file_path, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)
                        
                        cached_time = cache_data.get('timestamp', 0)
                        ttl = cache_data.get('ttl', self.default_ttl)
                        
                        if current_time - cached_time > ttl:
                            operation_stats['expired'] += 1
                        
                        # Track oldest/newest
                        if cached_time < oldest_time:
                            oldest_time = cached_time
                        if cached_time > newest_time:
                            newest_time = cached_time
                            
                    except (OSError, json.JSONDecodeError, KeyError):
                        pass
            
            if operation_stats['files'] > 0:
                stats['by_operation'][operation] = operation_stats
        
        # Convert timestamps to readable dates
        if oldest_time != float('inf'):
            stats['oldest_entry'] = datetime.fromtimestamp(oldest_time).isoformat()
        if newest_time > 0:
            stats['newest_entry'] = datetime.fromtimestamp(newest_time).isoformat()
        
        return stats

class CachedApifyInstagramScraper:
    """
    Wrapper around ApifyInstagramScraper that adds caching functionality
    """
    
    def __init__(self, api_token: str, cache_ttl: int = 3600):
        """
        Initialize cached scraper
        
        Args:
            api_token: Apify API token
            cache_ttl: Default cache time-to-live in seconds (1 hour default)
        """
        from .apify_scraper import ApifyInstagramScraper
        
        self.scraper = ApifyInstagramScraper(api_token)
        self.cache = ApifyCache(default_ttl=cache_ttl)
        
        logger.info("CachedApifyInstagramScraper initialized")
    
    def scrape_user_posts(self, username: str, limit: int = 50, include_stories: bool = False, 
                         use_cache: bool = True, cache_ttl: Optional[int] = None) -> List[Dict]:
        """
        Scrape user posts with caching
        
        Args:
            username: Instagram username
            limit: Maximum number of posts
            include_stories: Whether to include stories
            use_cache: Whether to use cached results
            cache_ttl: Cache TTL override
            
        Returns:
            List of post dictionaries
        """
        params = {
            'username': username,
            'limit': limit,
            'include_stories': include_stories
        }
        
        # Try to get from cache first
        if use_cache:
            cached_result = self.cache.get('user_posts', params, cache_ttl)
            if cached_result is not None:
                logger.info(f"Using cached results for @{username} ({len(cached_result)} posts)")
                return cached_result
        
        # Cache miss - fetch from API
        logger.info(f"Fetching fresh data from Apify for @{username}")
        result = self.scraper.scrape_user_posts(username, limit, include_stories)
        
        # Cache the result
        if result and use_cache:
            self.cache.set('user_posts', params, result, cache_ttl)
        
        return result
    
    def scrape_post_urls(self, urls: List[str], use_cache: bool = True, 
                        cache_ttl: Optional[int] = None) -> List[Dict]:
        """
        Scrape specific post URLs with caching
        
        Args:
            urls: List of Instagram post URLs
            use_cache: Whether to use cached results
            cache_ttl: Cache TTL override
            
        Returns:
            List of post dictionaries
        """
        params = {
            'urls': sorted(urls)  # Sort for consistent cache keys
        }
        
        # Try to get from cache first
        if use_cache:
            cached_result = self.cache.get('post_urls', params, cache_ttl)
            if cached_result is not None:
                logger.info(f"Using cached results for {len(urls)} URLs")
                return cached_result
        
        # Cache miss - fetch from API
        logger.info(f"Fetching fresh data from Apify for {len(urls)} URLs")
        result = self.scraper.scrape_post_urls(urls)
        
        # Cache the result
        if result and use_cache:
            self.cache.set('post_urls', params, result, cache_ttl)
        
        return result
    
    def get_user_profile(self, username: str, use_cache: bool = True, 
                        cache_ttl: Optional[int] = None) -> Dict:
        """
        Get user profile with caching
        
        Args:
            username: Instagram username
            use_cache: Whether to use cached results
            cache_ttl: Cache TTL override (profiles cached longer by default)
            
        Returns:
            Profile dictionary
        """
        params = {'username': username}
        
        # Use longer cache for profiles (6 hours default)
        profile_ttl = cache_ttl or 21600
        
        # Try to get from cache first
        if use_cache:
            cached_result = self.cache.get('profile', params, profile_ttl)
            if cached_result is not None:
                logger.info(f"Using cached profile for @{username}")
                return cached_result
        
        # Cache miss - fetch from API
        logger.info(f"Fetching fresh profile from Apify for @{username}")
        result = self.scraper.get_user_profile(username)
        
        # Cache the result
        if result and use_cache:
            self.cache.set('profile', params, result, profile_ttl)
        
        return result
    
    def get_usage_info(self) -> Dict:
        """Get Apify usage info (not cached as it changes frequently)"""
        return self.scraper.get_usage_info()
    
    def clear_cache_for_user(self, username: str) -> int:
        """
        Clear all cached data for a specific user
        
        Args:
            username: Instagram username
            
        Returns:
            Number of cache entries removed
        """
        removed = 0
        
        # Clear user posts cache
        params = {'username': username}
        if self.cache.invalidate('user_posts', params):
            removed += 1
        
        # Clear profile cache
        if self.cache.invalidate('profile', params):
            removed += 1
        
        logger.info(f"Cleared {removed} cache entries for @{username}")
        return removed
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.get_cache_stats()
    
    def clear_expired_cache(self) -> int:
        """Clear expired cache entries"""
        return self.cache.clear_expired()