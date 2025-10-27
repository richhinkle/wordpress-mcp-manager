#!/usr/bin/env python3
"""
Test different Instagram image URL variants to see if any work
"""
import requests
import re

def test_instagram_url_variants():
    # Original Instagram URL that's getting blocked
    original_url = "https://instagram.fabe1-1.fna.fbcdn.net/v/t51.2885-15/570354977_18131122888467505_2563450616446420131_n.jpg?stp=dst-jpg_e35_s1080x1080_sh0.08_tt6&_nc_ht=instagram.fabe1-1.fna.fbcdn.net&_nc_cat=101&_nc_oc=Q6cZ2QFwhDAqjmN46zuI1GqLMx13q84LKRDixBEwh-ufc6LaEZNofby0di43qM_btjmpKzfcbrhubfcKQuoO5xKo9f2R&_nc_ohc=JMi73C_YqN8Q7kNvwHOZflA&_nc_gid=SecD1btQQXdS3CkUi6BovA&edm=APs17CUBAAAA&ccb=7-5&oh=00_Afcha56Ip0w0EWbqsAgvH12_b5uPO6xIKDBxJD0OReg&oe=68FF6019&_nc_sid=10d13b"
    
    print(f"Original URL: {original_url[:100]}...")
    
    # Extract the base image ID and try different formats
    # Pattern: /v/t51.2885-15/IMAGE_ID_n.jpg
    match = re.search(r'/v/t51\.2885-15/(\d+_\d+_\d+)_n\.jpg', original_url)
    if not match:
        print("Could not extract image ID from URL")
        return
    
    image_id = match.group(1)
    print(f"Extracted image ID: {image_id}")
    
    # Try different URL variants
    variants = [
        # Simplified URL without query parameters
        f"https://instagram.fabe1-1.fna.fbcdn.net/v/t51.2885-15/{image_id}_n.jpg",
        
        # Different size variants
        f"https://instagram.fabe1-1.fna.fbcdn.net/v/t51.2885-15/{image_id}_n.jpg?stp=dst-jpg_e35_s640x640_sh0.08",
        f"https://instagram.fabe1-1.fna.fbcdn.net/v/t51.2885-15/{image_id}_n.jpg?stp=dst-jpg_e35_s480x480_sh0.08",
        
        # Different CDN endpoints
        f"https://scontent.cdninstagram.com/v/t51.2885-15/{image_id}_n.jpg",
        f"https://scontent-atl3-2.cdninstagram.com/v/t51.2885-15/{image_id}_n.jpg",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.instagram.com/',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    }
    
    for i, variant in enumerate(variants):
        print(f"\nTesting variant {i+1}: {variant[:80]}...")
        try:
            response = requests.get(variant, headers=headers, timeout=10)
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type', 'Unknown')}")
            print(f"  Content-Length: {response.headers.get('content-length', 'Unknown')}")
            
            if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
                print(f"  ✅ SUCCESS! This variant works!")
                return variant
            else:
                print(f"  ❌ Failed")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n❌ All variants failed. Instagram is blocking all access.")
    return None

if __name__ == "__main__":
    working_url = test_instagram_url_variants()
    if working_url:
        print(f"\n🎉 Found working URL: {working_url}")
    else:
        print(f"\n💡 Suggestion: Use Apify's browser automation to download images")