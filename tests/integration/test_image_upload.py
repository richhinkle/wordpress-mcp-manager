#!/usr/bin/env python3
"""
Test script to verify image upload functionality
"""
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.image_cache import ImageCache
from src.utils.wordpress_media import WordPressMediaUploader

def test_image_upload():
    """Test the complete image upload workflow"""
    
    # Test Instagram image URL (from your screenshots)
    test_image_url = "https://scontent-lax3-2.cdninstagram.com/v/t51.2885-15/464254203_18130555888467505_2612778206399448381_n.jpg"
    
    print("🧪 Testing Image Upload Workflow")
    print("=" * 50)
    
    # Step 1: Test image caching
    print("1️⃣ Testing image caching...")
    cache_manager = ImageCache()
    
    success, cache_path, error = cache_manager.cache_image(test_image_url)
    
    if success:
        print(f"✅ Image cached successfully: {cache_path}")
        image_info = cache_manager.get_image_info(cache_path)
        print(f"   Size: {image_info.get('size_mb', 0)} MB")
        print(f"   Type: {image_info.get('mime_type', 'unknown')}")
    else:
        print(f"❌ Image caching failed: {error}")
        return False
    
    # Step 2: Test WordPress credentials
    print("\n2️⃣ Testing WordPress credentials...")
    wordpress_url = os.getenv('WORDPRESS_URL', '').replace('/wp-json/mcp/v1/sse', '')
    username = os.getenv('WORDPRESS_USERNAME', '')
    password = os.getenv('WORDPRESS_PASSWORD', '')
    
    print(f"   WordPress URL: {wordpress_url}")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password) if password else 'NOT SET'}")
    
    if not all([wordpress_url, username, password]):
        print("❌ WordPress credentials incomplete!")
        return False
    
    # Step 3: Test WordPress upload
    print("\n3️⃣ Testing WordPress upload...")
    wp_uploader = WordPressMediaUploader(
        wordpress_url=wordpress_url,
        username=username,
        password=password
    )
    
    result = wp_uploader.upload_cached_image(
        cache_path=cache_path,
        filename="test_instagram_image.jpg",
        alt_text="Test Instagram image upload",
        caption="Test upload from Instagram import system"
    )
    
    if result['success']:
        print(f"✅ WordPress upload successful!")
        print(f"   Media ID: {result['media_id']}")
        print(f"   URL: {result['url']}")
    else:
        print(f"❌ WordPress upload failed: {result['error']}")
        return False
    
    print("\n🎉 All tests passed! Image upload workflow is working.")
    return True

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    test_image_upload()