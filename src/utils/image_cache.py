#!/usr/bin/env python3
"""
Image Cache System for Instagram Images
Uses our breakthrough download method to cache Instagram images locally
"""

import os
import hashlib
import requests
import logging
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class InstagramImageCache:
    """
    Cache system for Instagram images using our breakthrough download method
    """
    
    def __init__(self, cache_dir: str = "static/cached_images"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup session with Instagram-friendly headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.instagram.com/',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1',
            'Connection': 'keep-alive'
        })
    
    def _get_cache_filename(self, instagram_url: str) -> str:
        """Generate a cache filename from Instagram URL"""
        # Create a hash of the URL for consistent filename
        url_hash = hashlib.md5(instagram_url.encode()).hexdigest()
        
        # Extract original filename if possible
        parsed = urlparse(instagram_url)
        path_parts = parsed.path.split('/')
        original_name = path_parts[-1] if path_parts else 'image'
        
        # Remove query parameters from original name
        if '?' in original_name:
            original_name = original_name.split('?')[0]
        
        # Ensure it has an extension
        if not original_name.endswith(('.jpg', '.jpeg', '.png', '.webp')):
            original_name += '.jpg'
        
        # Combine hash with original name for uniqueness
        return f"{url_hash}_{original_name}"
    
    def _download_instagram_image(self, instagram_url: str) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """
        Download Instagram image using our breakthrough method
        """
        try:
            # Get Instagram homepage for cookies (helps with success rate)
            self.session.get('https://www.instagram.com/', timeout=10)
            
            # Download the image
            response = self.session.get(instagram_url, timeout=30)
            response.raise_for_status()
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully downloaded {len(response.content)} bytes from Instagram")
                return True, response.content, None
            else:
                error_msg = f"HTTP {response.status_code}"
                logger.warning(f"⚠️ Download failed: {error_msg}")
                return False, None, error_msg
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(f"❌ Download error: {error_msg}")
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"❌ Unexpected error: {error_msg}")
            return False, None, error_msg
    
    def get_cached_image_url(self, instagram_url: str, force_refresh: bool = False) -> Optional[str]:
        """
        Get cached image URL, downloading if necessary
        
        Args:
            instagram_url: Original Instagram CDN URL
            force_refresh: Force re-download even if cached
            
        Returns:
            Local cached image URL or None if failed
        """
        try:
            cache_filename = self._get_cache_filename(instagram_url)
            cache_path = self.cache_dir / cache_filename
            
            # Check if already cached and not forcing refresh
            if cache_path.exists() and not force_refresh:
                logger.info(f"📁 Using cached image: {cache_filename}")
                return f"/cached_images/{cache_filename}"
            
            # Download the image
            logger.info(f"📥 Downloading Instagram image: {instagram_url[:80]}...")
            success, image_data, error = self._download_instagram_image(instagram_url)
            
            if success and image_data:
                # Save to cache
                with open(cache_path, 'wb') as f:
                    f.write(image_data)
                
                logger.info(f"💾 Cached image: {cache_filename} ({len(image_data)} bytes)")
                return f"/cached_images/{cache_filename}"
            else:
                logger.error(f"❌ Failed to download image: {error}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Cache error: {e}")
            return None
    
    def cache_multiple_images(self, instagram_urls: list) -> dict:
        """
        Cache multiple Instagram images
        
        Args:
            instagram_urls: List of Instagram CDN URLs
            
        Returns:
            Dictionary mapping original URLs to cached URLs
        """
        results = {}
        
        for url in instagram_urls:
            cached_url = self.get_cached_image_url(url)
            results[url] = cached_url
        
        return results
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        try:
            cache_files = list(self.cache_dir.glob('*'))
            total_size = sum(f.stat().st_size for f in cache_files if f.is_file())
            
            return {
                'total_files': len(cache_files),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'cache_dir': str(self.cache_dir)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    def clear_cache(self) -> int:
        """Clear all cached images"""
        try:
            cache_files = list(self.cache_dir.glob('*'))
            removed_count = 0
            
            for cache_file in cache_files:
                if cache_file.is_file():
                    cache_file.unlink()
                    removed_count += 1
            
            logger.info(f"🗑️ Cleared {removed_count} cached images")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0

# Global cache instance
image_cache = InstagramImageCache()