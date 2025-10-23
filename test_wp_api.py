#!/usr/bin/env python3
"""
Test WordPress REST API access
"""
import os
import requests
import base64

def test_wp_api():
    """Test basic WordPress REST API access"""
    
    print("🧪 Testing WordPress REST API Access")
    print("=" * 50)
    
    # Get credentials
    wordpress_url = os.getenv('WORDPRESS_URL', '').replace('/wp-json/mcp/v1/sse', '')
    username = os.getenv('WORDPRESS_USERNAME', '')
    password = os.getenv('WORDPRESS_PASSWORD', '')
    
    print(f"WordPress URL: {wordpress_url}")
    print(f"Username: {username}")
    
    # Create auth header
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded_credentials}"
    
    # Test 1: Check if REST API is accessible
    print("\n1️⃣ Testing REST API accessibility...")
    try:
        response = requests.get(f"{wordpress_url}/wp-json/wp/v2/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ REST API is accessible")
        else:
            print(f"   ❌ REST API returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ REST API connection failed: {e}")
        return False
    
    # Test 2: Check authentication
    print("\n2️⃣ Testing authentication...")
    try:
        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }
        response = requests.get(f"{wordpress_url}/wp-json/wp/v2/users/me", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Authenticated as: {user_data.get('name', 'Unknown')}")
        else:
            print(f"   ❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Authentication test failed: {e}")
        return False
    
    # Test 3: Check media upload permissions
    print("\n3️⃣ Testing media upload permissions...")
    try:
        response = requests.get(f"{wordpress_url}/wp-json/wp/v2/media", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Media endpoint accessible")
        else:
            print(f"   ❌ Media endpoint returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Media endpoint test failed: {e}")
        return False
    
    print("\n🎉 All WordPress API tests passed!")
    return True

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    test_wp_api()