#!/usr/bin/env python3
"""
Example: How to use the bulk import feature
"""

import requests
import json

# Your WordPress MCP Manager URL
BASE_URL = "http://localhost:5000"

def bulk_import_instagram_user(username, limit=10):
    """
    Bulk import Instagram posts using the API endpoint
    """
    
    # Remove @ if present
    username = username.replace('@', '')
    
    # API endpoint for bulk import
    url = f"{BASE_URL}/api/instagram/apify/bulk-import"
    
    # Request payload
    payload = {
        "username": username,
        "limit": limit
    }
    
    print(f"🚀 Starting bulk import for @{username} (limit: {limit})")
    
    try:
        # Make the API call
        response = requests.post(url, json=payload, timeout=300)  # 5 minute timeout
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"✅ Success! Imported {result.get('imported_count', 0)} posts")
                print(f"📊 Scraped: {result.get('scraped_count', 0)} posts")
                print(f"📝 Message: {result.get('message', '')}")
                
                # Show imported posts
                imported_posts = result.get('imported_posts', [])
                if imported_posts:
                    print(f"\n📋 Imported Posts:")
                    for i, post in enumerate(imported_posts, 1):
                        print(f"   {i}. {post.get('title', 'Untitled')} (ID: {post.get('wordpress_id')})")
                
                return result
            else:
                print(f"❌ Import failed: {result.get('error', 'Unknown error')}")
                return None
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - bulk import may still be running")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_apify_status():
    """Check if Apify is configured and working"""
    
    url = f"{BASE_URL}/api/instagram/apify/status"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('available'):
                print("✅ Apify integration is ready")
                
                usage = result.get('usage_info', {})
                if usage:
                    print(f"📊 Account info: {usage}")
                
                cache = result.get('cache_stats', {})
                if cache:
                    print(f"💾 Cache stats: {cache}")
                
                return True
            else:
                print(f"❌ Apify not available: {result.get('error')}")
                return False
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Instagram Bulk Import Example")
    print("=" * 50)
    
    # Step 1: Check Apify status
    print("\n1️⃣ Checking Apify status...")
    if not check_apify_status():
        print("❌ Apify not ready. Check your APIFY_API_TOKEN in .env file")
        exit(1)
    
    # Step 2: Bulk import
    print("\n2️⃣ Starting bulk import...")
    result = bulk_import_instagram_user("example_user", limit=5)
    
    if result:
        print("\n🎉 Bulk import completed successfully!")
        print("💡 Check your WordPress admin to see the imported posts as drafts")
    else:
        print("\n❌ Bulk import failed")