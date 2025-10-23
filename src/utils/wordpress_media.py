"""
WordPress media upload utilities using cached images
"""
import base64
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any
import requests
import json

class WordPressMediaUploader:
    def __init__(self, wordpress_url: str, username: str, password: str):
        self.wordpress_url = wordpress_url.rstrip('/')
        self.username = username
        self.password = password
        self.auth_header = self._create_auth_header()
    
    def _create_auth_header(self) -> str:
        """Create basic auth header for WordPress API"""
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"
    
    def upload_cached_image(self, 
                          cache_path: Path, 
                          filename: Optional[str] = None,
                          alt_text: Optional[str] = None,
                          caption: Optional[str] = None,
                          description: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a cached image to WordPress media library
        
        Args:
            cache_path: Path to cached image file
            filename: Custom filename (optional, uses cache filename if not provided)
            alt_text: Alt text for accessibility
            caption: Image caption
            description: Image description
            
        Returns:
            Dictionary with upload result
        """
        if not cache_path.exists():
            return {
                'success': False,
                'error': f'Cached image not found: {cache_path}'
            }
        
        try:
            # Determine filename and mime type
            if not filename:
                filename = cache_path.name
            
            mime_type, _ = mimetypes.guess_type(str(cache_path))
            if not mime_type:
                mime_type = 'image/jpeg'
            
            # Read image data
            with open(cache_path, 'rb') as f:
                image_data = f.read()
            
            # Prepare headers
            headers = {
                'Authorization': self.auth_header,
                'Content-Type': mime_type,
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
            
            # Upload to WordPress
            upload_url = f"{self.wordpress_url}/wp-json/wp/v2/media"
            
            # Debug logging
            print(f"🔄 Uploading to: {upload_url}")
            print(f"🔄 Filename: {filename}")
            print(f"🔄 Content-Type: {mime_type}")
            print(f"🔄 Image size: {len(image_data)} bytes")
            
            response = requests.post(
                upload_url,
                headers=headers,
                data=image_data,
                timeout=30
            )
            
            print(f"🔄 Upload response status: {response.status_code}")
            if response.status_code != 201:
                print(f"❌ Upload failed response: {response.text}")
            else:
                print(f"✅ Upload successful!")
            
            if response.status_code == 201:
                media_data = response.json()
                media_id = media_data['id']
                
                # Update media metadata if provided
                if alt_text or caption or description:
                    self._update_media_metadata(media_id, alt_text, caption, description)
                
                return {
                    'success': True,
                    'media_id': media_id,
                    'url': media_data['source_url'],
                    'filename': filename,
                    'mime_type': mime_type,
                    'wordpress_data': media_data
                }
            else:
                return {
                    'success': False,
                    'error': f'WordPress upload failed: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error uploading image: {str(e)}'
            }
    
    def _update_media_metadata(self, 
                             media_id: int, 
                             alt_text: Optional[str] = None,
                             caption: Optional[str] = None,
                             description: Optional[str] = None):
        """Update media item metadata"""
        try:
            update_data = {}
            
            if alt_text:
                update_data['alt_text'] = alt_text
            if caption:
                update_data['caption'] = {'raw': caption}
            if description:
                update_data['description'] = {'raw': description}
            
            if update_data:
                headers = {
                    'Authorization': self.auth_header,
                    'Content-Type': 'application/json'
                }
                
                update_url = f"{self.wordpress_url}/wp-json/wp/v2/media/{media_id}"
                requests.post(update_url, headers=headers, json=update_data, timeout=10)
                
        except Exception as e:
            # Don't fail the main upload if metadata update fails
            print(f"Warning: Failed to update media metadata: {e}")
    
    def upload_instagram_image_to_wordpress(self, 
                                          image_url: str,
                                          post_data: Dict[str, Any],
                                          cache_manager) -> Dict[str, Any]:
        """
        Complete workflow: cache Instagram image and upload to WordPress
        
        Args:
            image_url: Instagram image URL
            post_data: Instagram post data (for metadata)
            cache_manager: ImageCache instance
            
        Returns:
            Dictionary with complete upload result
        """
        try:
            # First, ensure image is cached
            success, cache_path, error = cache_manager.cache_image(image_url)
            if not success:
                return {
                    'success': False,
                    'error': f'Failed to cache image: {error}'
                }
            
            # Generate filename from Instagram data
            username = post_data.get('username', 'instagram')
            shortcode = post_data.get('shortcode', '')
            if shortcode:
                filename = f"instagram_{username}_{shortcode}_{cache_path.name}"
            else:
                # Use a hash of the URL as fallback
                import hashlib
                url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
                filename = f"instagram_{username}_{url_hash}_{cache_path.name}"
            
            # Prepare metadata
            alt_text = post_data.get('caption', '')[:100] + '...' if len(post_data.get('caption', '')) > 100 else post_data.get('caption', '')
            caption = f"Instagram post by @{username}"
            description = f"Imported from Instagram: {post_data.get('post_url', '')}"
            
            # Upload to WordPress
            result = self.upload_cached_image(
                cache_path=cache_path,
                filename=filename,
                alt_text=alt_text,
                caption=caption,
                description=description
            )
            
            if result['success']:
                result['cache_path'] = str(cache_path)
                result['instagram_data'] = post_data
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error in Instagram to WordPress workflow: {str(e)}'
            }