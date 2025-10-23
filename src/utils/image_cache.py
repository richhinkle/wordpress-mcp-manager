"""
Image caching utility for Instagram images
"""
import os
import hashlib
import requests
from pathlib import Path
from typing import Optional, Tuple
import mimetypes
from urllib.parse import urlparse

class ImageCache:
    def __init__(self, cache_dir: str = None):
        if cache_dir is None:
            # Get the project root directory (go up from src/utils to project root)
            project_root = Path(__file__).parent.parent.parent
            cache_dir = project_root / "cache" / "images"
        else:
            cache_dir = Path(cache_dir)
        
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_path(self, image_url: str) -> Path:
        """Generate cache file path based on URL hash"""
        url_hash = hashlib.md5(image_url.encode()).hexdigest()
        
        # Try to get file extension from URL
        parsed_url = urlparse(image_url)
        path_parts = parsed_url.path.split('.')
        if len(path_parts) > 1:
            extension = path_parts[-1].split('?')[0]  # Remove query params
            if extension.lower() in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
                return self.cache_dir / f"{url_hash}.{extension}"
        
        # Default to jpg if no extension found
        return self.cache_dir / f"{url_hash}.jpg"
    
    def is_cached(self, image_url: str) -> bool:
        """Check if image is already cached"""
        cache_path = self._get_cache_path(image_url)
        return cache_path.exists()
    
    def get_cached_path(self, image_url: str) -> Optional[Path]:
        """Get path to cached image if it exists"""
        cache_path = self._get_cache_path(image_url)
        return cache_path if cache_path.exists() else None
    
    def cache_image(self, image_url: str, force_refresh: bool = False) -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        Cache an image from URL
        
        Returns:
            (success, cache_path, error_message)
        """
        cache_path = self._get_cache_path(image_url)
        
        # Skip if already cached and not forcing refresh
        if cache_path.exists() and not force_refresh:
            return True, cache_path, None
        
        try:
            # Enhanced Instagram-appropriate headers to bypass restrictions
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.instagram.com/',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'image',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # Use a session to maintain cookies and look more like a real browser
            session = requests.Session()
            session.headers.update(headers)
            
            # First make a request to Instagram to get cookies
            try:
                session.get('https://www.instagram.com/', timeout=10)
            except:
                pass  # Ignore errors, just trying to get cookies
            
            response = session.get(image_url, timeout=15, stream=True)
            response.raise_for_status()
            
            # Verify it's actually an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                return False, None, f"URL does not return an image (content-type: {content_type})"
            
            # Save to cache
            with open(cache_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True, cache_path, None
            
        except requests.exceptions.RequestException as e:
            return False, None, f"Failed to download image: {str(e)}"
        except Exception as e:
            return False, None, f"Error caching image: {str(e)}"
    
    def get_image_info(self, cache_path: Path) -> dict:
        """Get basic info about cached image"""
        if not cache_path.exists():
            return {}
        
        stat = cache_path.stat()
        mime_type, _ = mimetypes.guess_type(str(cache_path))
        
        return {
            'path': str(cache_path),
            'size_bytes': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'mime_type': mime_type,
            'filename': cache_path.name
        }
    
    def cleanup_old_images(self, max_age_days: int = 30):
        """Remove cached images older than specified days"""
        import time
        
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        removed_count = 0
        for image_file in self.cache_dir.glob("*"):
            if image_file.is_file():
                file_age = current_time - image_file.stat().st_mtime
                if file_age > max_age_seconds:
                    image_file.unlink()
                    removed_count += 1
        
        return removed_count
    
    def get_cache_stats(self) -> dict:
        """Get statistics about the image cache"""
        if not self.cache_dir.exists():
            return {'total_images': 0, 'total_size_mb': 0}
        
        total_size = 0
        image_count = 0
        
        for image_file in self.cache_dir.glob("*"):
            if image_file.is_file():
                total_size += image_file.stat().st_size
                image_count += 1
        
        return {
            'total_images': image_count,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': str(self.cache_dir)
        }