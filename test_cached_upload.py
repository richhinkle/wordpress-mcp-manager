#!/usr/bin/env python3
"""
Test script to verify cached image upload functionality
"""
import os
from pathlib import Path
from src.utils.image_cache import ImageCache
from src.utils.wordpress_media import WordPressMediaUploader

def test_cached_upload():
    """Test uploading an existing cached image to WordPress"""
    
    print("🧪 Testing Cached Image Upload")
    print("=" * 50)
    
    # Check for existing cached images
    cache_manager = ImageCache()
    cache_dir = Path("cache/images")
    
    if not cache_dir.exists():
        print("❌ No cache directory found")
        return False
    
    cached_files = list(cache_dir.glob("*.jpg"))
    if not cached_files:
        print("❌ No cached images found")
        return False
    
    # Use the first cached image
    test_image = cached_files[0]
    print(f"📁 Using cached image: {test_image}")
    
    # Get image info
    image_info = cache_manager.get_image_info(test_image)
    print(f"   Size: {image_info.get('size_mb', 0)} MB")
    print(f"   Type: {image_info.get('mime_type', 'unknown')}")
    
    # Test WordPress credentials
    print("\n🔑 Testing WordPress credentials...")
    wordpress_url = os.getenv('WORDPRESS_URL', '').replace('/wp-json/mcp/v1/sse', '')
    username = os.getenv('WORDPRESS_USERNAME', '')
    password = os.getenv('WORDPRESS_PASSWORD', '')
    
    print(f"   WordPress URL: {wordpress_url}")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password) if password else 'NOT SET'}")
    
    if not all([wordpress_url, username, password]):
        print("❌ WordPress credentials incomplete!")
        return False
    
    # Test WordPress upload
    print("\n📤 Testing WordPress upload...")
    wp_uploader = WordPressMediaUploader(
        wordpress_url=wordpress_url,
        username=username,
        password=password
    )
    
    result = wp_uploader.upload_cached_image(
        cache_path=test_image,
        filename=f"test_cached_instagram_{test_image.name}",
        alt_text="Test cached Instagram image upload",
        caption="Test upload from cached Instagram image",
        description="Testing the cached image upload workflow"
    )
    
    if result['success']:
        print(f"✅ WordPress upload successful!")
        print(f"   Media ID: {result['media_id']}")
        print(f"   URL: {result['url']}")
        print(f"   Filename: {result['filename']}")
    else:
        print(f"❌ WordPress upload failed: {result['error']}")
        return False
    
    print("\n🎉 Cached image upload test passed!")
    return True

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    test_cached_upload()