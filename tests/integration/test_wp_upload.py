#!/usr/bin/env python3
"""
Test WordPress REST API image upload directly
"""
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.wordpress_media import WordPressMediaUploader
from src.utils.image_cache import ImageCache

def test_wordpress_upload():
    # Initialize
    cache_manager = ImageCache()
    wp_uploader = WordPressMediaUploader(
        wordpress_url=os.getenv('WORDPRESS_URL', '').replace('/wp-json/mcp/v1/sse', ''),
        username=os.getenv('WORDPRESS_USERNAME', ''),
        password=os.getenv('WORDPRESS_PASSWORD', '')
    )
    
    # Test image URL
    test_image_url = "https://instagram.fabe1-1.fna.fbcdn.net/v/t51.2885-15/570354977_18131122888467505_2563450616446420131_n.jpg?stp=dst-jpg_e35_s1080x1080_sh0.08_tt6&_nc_ht=instagram.fabe1-1.fna.fbcdn.net&_nc_cat=101&_nc_oc=Q6cZ2QFwhDAqjmN46zuI1GqLMx13q84LKRDixBEwh-ufc6LaEZNofby0di43qM_btjmpKzfcbrhubfcKQuoO5xKo9f2R&_nc_ohc=JMi73C_YqN8Q7kNvwHOZflA&_nc_gid=SecD1btQQXdS3CkUi6BovA&edm=APs17CUBAAAA&ccb=7-5&oh=00_Afcha56Ip0w0EWbqsAgvH12_b5uPO6xIKDBxJD0OReg&oe=68FF6019&_nc_sid=10d13b"
    
    post_data = {
        'shortcode': 'test_upload',
        'username': 'example_user',
        'caption': 'Test upload via REST API'
    }
    
    print("Testing WordPress REST API upload...")
    print(f"WordPress URL: {os.getenv('WORDPRESS_URL', '').replace('/wp-json/mcp/v1/sse', '')}")
    print(f"Username: {os.getenv('WORDPRESS_USERNAME', '')}")
    print(f"Image URL: {test_image_url[:100]}...")
    
    try:
        result = wp_uploader.upload_instagram_image_to_wordpress(
            image_url=test_image_url,
            post_data=post_data,
            cache_manager=cache_manager
        )
        
        print(f"\nResult: {result}")
        
        if result['success']:
            print(f"✅ Upload successful!")
            print(f"   Media ID: {result['media_id']}")
            print(f"   URL: {result['url']}")
        else:
            print(f"❌ Upload failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_wordpress_upload()