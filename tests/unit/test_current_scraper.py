#!/usr/bin/env python3
"""
Test current Instagram scraper to see what image URLs we get
"""
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.integrations.instagram.apify_scraper import ApifyInstagramScraper
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv('APIFY_API_TOKEN')

if api_token:
    scraper = ApifyInstagramScraper(api_token)
    try:
        print("🔍 Testing current Instagram scraper...")
        posts = scraper.scrape_user_posts('example_user', limit=1)
        
        if posts:
            post = posts[0]
            print(f"\n📱 Found post: {post.get('shortcode', 'unknown')}")
            print(f"📸 Image URL: {post.get('image_url', 'None')}")
            
            # Check raw data
            raw_data = post.get('raw_data', {})
            if raw_data:
                print(f"🔍 Raw displayUrl: {raw_data.get('displayUrl', 'None')}")
                print(f"🔍 Raw keys: {list(raw_data.keys())}")
            
            # Check if it's an Apify CDN URL
            image_url = post.get('image_url', '')
            if 'apify' in image_url.lower() or 'cdn-cms.apify.com' in image_url:
                print("✅ Apify CDN URL detected!")
            else:
                print("❌ Not an Apify CDN URL - it's Instagram CDN")
                
        else:
            print("❌ No posts found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ No API token found")