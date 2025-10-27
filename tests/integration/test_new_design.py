#!/usr/bin/env python3
"""
Test the new Instagram post design
"""

import requests
import json

# Test the new design with a single post
def test_new_design():
    print("🎨 Testing New Instagram Post Design")
    print("=" * 50)
    
    # API endpoint for bulk import
    url = "http://localhost:5000/api/instagram/apify/bulk-import"
    
    # Request payload - just 1 post to test
    payload = {
        "username": "example_user",
        "limit": 1
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"✅ Success! Imported {result.get('imported_count', 0)} posts")
                print(f"📝 Message: {result.get('message', '')}")
                
                imported_posts = result.get('imported_posts', [])
                if imported_posts:
                    post = imported_posts[0]
                    print(f"\n📋 Test Post:")
                    print(f"   Title: {post.get('title', 'Untitled')}")
                    print(f"   WordPress ID: {post.get('wordpress_id')}")
                    print(f"   Status: {post.get('status')}")
                    
                    print(f"\n🎯 Check WordPress admin to see the new design!")
                    print(f"   Go to: https://your-site.com/wp-admin/post.php?post={post.get('wordpress_id')}&action=edit")
                
                return True
            else:
                print(f"❌ Import failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_new_design()