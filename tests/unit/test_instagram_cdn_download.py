#!/usr/bin/env python3
"""
Test downloading from Instagram CDN with various approaches
"""
import requests
import base64

# Use the Instagram CDN URL from our test
test_url = "https://scontent-ord5-1.cdninstagram.com/v/t51.2885-15/569838232_18131229967467505_5496964582419516716_n.jpg?stp=dst-jpg_e15_fr_p1080x1080_tt6&_nc_ht=scontent-ord5-1.cdninstagram.com&_nc_cat=101&_nc_oc=Q6cZ2QFxquFIjVzK1l9wxoLxreEdWWjj0KNWnISjdvkLFftJYw0WcHqjPiiKMOZaAuV5lAA&_nc_ohc=cmMz51YbnP8Q7kNvwH9UPhA&_nc_gid=bkb3mVCImodSW46We5-Z_Q&edm=APs17CUBAAAA&ccb=7-5&oh=00_AfexFAkg_LKHBjuoBdA5LT-_j5kSJeHohTVUENcuVhqiYQ&oe=690041C0&_nc_sid=10d13b"

print("🧪 Testing Instagram CDN download approaches...")
print(f"🔗 URL: {test_url[:100]}...")

# Method 1: Basic request
print("\n1️⃣ Basic request:")
try:
    response = requests.get(test_url, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Success! Downloaded {len(response.content)} bytes")
    else:
        print(f"   ❌ Failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Method 2: With Instagram-like headers
print("\n2️⃣ With Instagram headers:")
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
    'Sec-Fetch-Site': 'cross-site'
}

try:
    response = requests.get(test_url, headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Success! Downloaded {len(response.content)} bytes")
    else:
        print(f"   ❌ Failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Method 3: With session and cookies
print("\n3️⃣ With session and cookies:")
try:
    session = requests.Session()
    session.headers.update(headers)
    
    # First get Instagram homepage to get cookies
    session.get('https://www.instagram.com/', timeout=10)
    
    # Then try to get the image
    response = session.get(test_url, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Success! Downloaded {len(response.content)} bytes")
        print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
    else:
        print(f"   ❌ Failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n🎯 Conclusion: If any method succeeded, we can use it in our image downloader!")