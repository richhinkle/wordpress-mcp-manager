#!/usr/bin/env python3
"""
Test Instagram Integration with WordPress MCP Manager
"""

import requests
import json
from instagram_manual_import import InstagramManualImport

def test_instagram_import():
    """Test the Instagram import functionality"""
    
    print("=" * 60)
    print("Testing Instagram Integration")
    print("=" * 60)
    
    # Test 1: Manual Import System
    print("\n1. Testing Manual Import System...")
    importer = InstagramManualImport()
    
    # Create sample data
    sample_posts = [
        {
            'id': 'test_1',
            'shortcode': 'test_1',
            'caption': 'Test post from Example Business! 🎉 #example_business #signs #celebration',
            'image_url': 'https://via.placeholder.com/400x400/FF6B6B/FFFFFF?text=Card+My+Yard+1',
            'post_url': 'https://www.instagram.com/p/test1/',
            'hashtags': ['example_business', 'signs', 'celebration'],
            'timestamp': 1640995200,
            'date_posted': '2022-01-01 00:00:00',
            'extraction_method': 'test_data'
        },
        {
            'id': 'test_2', 
            'shortcode': 'test_2',
            'caption': 'Another amazing yard display! Perfect for birthdays 🎂 #birthday #yardgreetings #oviedo',
            'image_url': 'https://via.placeholder.com/400x400/4ECDC4/FFFFFF?text=Card+My+Yard+2',
            'post_url': 'https://www.instagram.com/p/test2/',
            'hashtags': ['birthday', 'yardgreetings', 'oviedo'],
            'timestamp': 1641081600,
            'date_posted': '2022-01-02 00:00:00',
            'extraction_method': 'test_data'
        }
    ]
    
    print(f"✅ Created {len(sample_posts)} sample Instagram posts")
    
    # Test 2: WordPress MCP Manager API (if running)
    print("\n2. Testing WordPress MCP Manager API...")
    
    try:
        # Check if the app is running
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ WordPress MCP Manager is running")
            
            # Test Instagram import endpoint
            print("\n3. Testing Instagram Import API...")
            
            import_response = requests.post(
                'http://localhost:5000/api/instagram/import-to-wordpress',
                json={'posts': sample_posts},
                timeout=30
            )
            
            if import_response.status_code == 200:
                result = import_response.json()
                print(f"✅ Import successful! Imported {result.get('imported_count', 0)} posts")
                
                # Show imported posts
                for i, imported in enumerate(result.get('imported_posts', []), 1):
                    wp_post = imported.get('wordpress_post', {})
                    print(f"  Post {i}: {wp_post.get('post_title', 'Unknown')} (ID: {wp_post.get('ID', 'Unknown')})")
            else:
                print(f"❌ Import failed: {import_response.status_code}")
                print(f"Response: {import_response.text}")
        else:
            print("❌ WordPress MCP Manager not responding")
            
    except requests.exceptions.ConnectionError:
        print("❌ WordPress MCP Manager not running (start with 'python run.py')")
    except Exception as e:
        print(f"❌ Error testing API: {e}")
    
    # Test 3: Chat Handler Integration
    print("\n4. Testing Chat Handler...")
    
    try:
        from chat_handler import WordPressChatHandler
        from app import WordPressMCPClient
        import os
        
        # Mock MCP client for testing
        class MockMCPClient:
            def create_post(self, **kwargs):
                return {'ID': 123, 'post_title': kwargs.get('title', 'Test Post')}
            
            def upload_media_from_url(self, **kwargs):
                return {'id': 456, 'url': kwargs.get('url', '')}
            
            def set_featured_image(self, post_id, media_id):
                return True
        
        mock_client = MockMCPClient()
        chat_handler = WordPressChatHandler(mock_client)
        
        # Test Instagram commands
        test_messages = [
            "instagram help",
            "import instagram post https://www.instagram.com/p/ABC123/",
            "import instagram posts https://www.instagram.com/p/ABC123/ https://www.instagram.com/p/DEF456/"
        ]
        
        for message in test_messages:
            print(f"\n  Testing: '{message}'")
            response = chat_handler.process_message(message)
            print(f"  Response type: {response.get('type', 'unknown')}")
            print(f"  Message: {response.get('message', 'No message')[:80]}...")
            if response.get('actions'):
                print(f"  Actions: {len(response['actions'])} available")
        
        print("✅ Chat handler integration working")
        
    except Exception as e:
        print(f"❌ Chat handler test failed: {e}")
    
    print("\n" + "=" * 60)
    print("Instagram Integration Test Complete!")
    print("=" * 60)
    
    print("\n🚀 Next Steps:")
    print("1. Start the WordPress MCP Manager: python run.py")
    print("2. Open http://localhost:5000 in your browser")
    print("3. Try these chat commands:")
    print("   - 'instagram help'")
    print("   - 'import instagram post [URL]'")
    print("4. Use real Instagram URLs from @example_user")

if __name__ == "__main__":
    test_instagram_import()