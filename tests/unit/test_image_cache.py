#!/usr/bin/env python3
"""
Test Instagram Image Caching System
"""

import requests
import json

def test_image_caching():
    print("🖼️ Testing Instagram Image Caching System")
    print("=" * 60)
    
    # Test Instagram CDN URL (from your example)
    test_url = "https://scontent-iad3-1.cdninstagram.com/v/t51.2885-15/561516685_18129700012467505_5306390062499970341_n.jpg?stp=dst-jpg_e35_s1080x1080_sh0.08_tt6&_nc_ht=scontent-iad3-1.cdninstagram.com&_nc_cat=101&_nc_oc=Q6cZ2QHH1xqNc_GQRDy2YfENb3cm28Rta_JVRMIpg0TBlBK_WbECVPw7bpLETCXM6SA1FSL_IYr4pCaAjYOZ9A9dF2EK&_nc_ohc=nqpVSbhMd80Q7kNvwEZ_Wvq&_nc_gid=1xuHV_cndsSHSkPJO_cKcw&edm=APs17CUBAAAA&ccb=7-5&oh=00_Afebjq7FFtXBILxOJMFPlSi8giG48vVWq96Hcz8GOOpuHg&oe=69008031&_nc_sid=10d13b"
    
    print(f"📸 Testing URL: {test_url[:80]}...")
    
    try:
        # Test caching endpoint
        response = requests.post(
            'http://localhost:5000/api/instagram/cache-image',
            json={'instagram_url': test_url},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"✅ Image cached successfully!")
                print(f"   Original: {result['original_url'][:80]}...")
                print(f"   Cached: {result['cached_url']}")
                
                # Test accessing the cached image
                cached_response = requests.get(f"http://localhost:5000{result['cached_url']}")
                
                if cached_response.status_code == 200:
                    print(f"✅ Cached image accessible: {len(cached_response.content)} bytes")
                else:
                    print(f"❌ Cached image not accessible: {cached_response.status_code}")
                
            else:
                print(f"❌ Caching failed: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test cache stats
    print(f"\n📊 Getting cache stats...")
    try:
        stats_response = requests.get('http://localhost:5000/api/instagram/image-cache/stats')
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            
            if stats.get('success'):
                cache_stats = stats['cache_stats']
                print(f"✅ Cache Stats:")
                print(f"   Files: {cache_stats.get('total_files', 0)}")
                print(f"   Size: {cache_stats.get('total_size_mb', 0)} MB")
                print(f"   Directory: {cache_stats.get('cache_dir', 'Unknown')}")
            else:
                print(f"❌ Stats failed: {stats.get('error')}")
        else:
            print(f"❌ Stats HTTP Error: {stats_response.status_code}")
            
    except Exception as e:
        print(f"❌ Stats test failed: {e}")

if __name__ == "__main__":
    test_image_caching()