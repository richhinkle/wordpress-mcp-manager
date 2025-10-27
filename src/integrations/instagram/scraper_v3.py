import requests
import json
import re
import time
from typing import List, Dict, Optional
from urllib.parse import quote

class InstagramScraperV3:
    def __init__(self):
        self.session = requests.Session()
        
        # More realistic headers to avoid detection
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest',
        })
    
    def get_user_posts_simple(self, username: str, max_posts: int = 12) -> List[Dict]:
        """
        Try to get Instagram posts using a simpler approach
        This method tries to extract data from the public page without GraphQL
        """
        try:
            print(f"Attempting to scrape @{username} using simple method...")
            
            # First, get the main page to establish session
            url = f"https://www.instagram.com/{username}/"
            
            # Add some delay to be respectful
            time.sleep(2)
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Successfully loaded Instagram page for @{username}")
                
                # Try to extract any JSON data from the page
                posts = self._extract_posts_from_page(response.text, username)
                
                if posts:
                    print(f"✅ Found {len(posts)} posts")
                    return posts[:max_posts]
                else:
                    print("❌ Could not extract posts from page")
                    # Try alternative method
                    return self._try_alternative_extraction(response.text, username)
            else:
                print(f"❌ Failed to load page. Status: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def _extract_posts_from_page(self, html: str, username: str) -> List[Dict]:
        """Extract posts from Instagram HTML page"""
        posts = []
        
        try:
            # Look for various JSON data patterns
            patterns = [
                r'window\._sharedData\s*=\s*({.*?});',
                r'"ProfilePage"\s*:\s*\[({.*?})\]',
                r'"user"\s*:\s*({.*?"edge_owner_to_timeline_media".*?})',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match)
                        extracted_posts = self._parse_json_for_posts(data, username)
                        if extracted_posts:
                            posts.extend(extracted_posts)
                            break
                    except json.JSONDecodeError:
                        continue
                
                if posts:
                    break
            
            return posts
            
        except Exception as e:
            print(f"Error extracting posts: {e}")
            return []
    
    def _try_alternative_extraction(self, html: str, username: str) -> List[Dict]:
        """Try alternative methods to extract post data"""
        try:
            # Look for image URLs in the HTML
            img_pattern = r'https://[^"]*\.(?:jpg|jpeg|png|webp)[^"]*'
            img_urls = re.findall(img_pattern, html)
            
            # Filter for Instagram CDN URLs
            instagram_imgs = [url for url in img_urls if 'cdninstagram' in url or 'fbcdn' in url]
            
            if instagram_imgs:
                print(f"Found {len(instagram_imgs)} potential Instagram images")
                
                # Create basic post objects
                posts = []
                for i, img_url in enumerate(instagram_imgs[:12]):  # Limit to 12
                    post = {
                        'id': f"scraped_{i}",
                        'shortcode': f"scraped_{i}",
                        'username': username,
                        'caption': f"Post from @{username}",
                        'image_url': img_url,
                        'post_url': f"https://www.instagram.com/{username}/",
                        'timestamp': int(time.time()),
                        'date_posted': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'likes': 0,
                        'comments': 0,
                        'hashtags': [],
                        'is_video': False,
                        'scraped_method': 'alternative'
                    }
                    posts.append(post)
                
                return posts
            
        except Exception as e:
            print(f"Alternative extraction failed: {e}")
        
        return []
    
    def _parse_json_for_posts(self, data: dict, username: str) -> List[Dict]:
        """Parse JSON data to extract posts"""
        posts = []
        
        try:
            # Navigate through possible JSON structures
            if 'entry_data' in data:
                profile_page = data.get('entry_data', {}).get('ProfilePage', [])
                if profile_page:
                    user_data = profile_page[0].get('graphql', {}).get('user', {})
                    timeline_media = user_data.get('edge_owner_to_timeline_media', {})
                    edges = timeline_media.get('edges', [])
                    
                    for edge in edges:
                        node = edge.get('node', {})
                        post = self._format_post_from_node(node, username)
                        if post:
                            posts.append(post)
            
            # Try direct user data
            elif 'edge_owner_to_timeline_media' in data:
                edges = data.get('edge_owner_to_timeline_media', {}).get('edges', [])
                for edge in edges:
                    node = edge.get('node', {})
                    post = self._format_post_from_node(node, username)
                    if post:
                        posts.append(post)
        
        except Exception as e:
            print(f"Error parsing JSON: {e}")
        
        return posts
    
    def _format_post_from_node(self, node: dict, username: str) -> Optional[Dict]:
        """Format a post node into our standard format"""
        try:
            post_id = node.get('id', '')
            shortcode = node.get('shortcode', '')
            
            if not shortcode:
                return None
            
            # Get caption
            caption_edges = node.get('edge_media_to_caption', {}).get('edges', [])
            caption = ''
            if caption_edges:
                caption = caption_edges[0].get('node', {}).get('text', '')
            
            # Extract hashtags
            hashtags = re.findall(r'#(\w+)', caption) if caption else []
            
            post = {
                'id': post_id,
                'shortcode': shortcode,
                'username': username,
                'caption': caption,
                'image_url': node.get('display_url', ''),
                'post_url': f"https://www.instagram.com/p/{shortcode}/",
                'timestamp': node.get('taken_at_timestamp', 0),
                'date_posted': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(node.get('taken_at_timestamp', 0))),
                'likes': node.get('edge_media_preview_like', {}).get('count', 0),
                'comments': node.get('edge_media_to_comment', {}).get('count', 0),
                'is_video': node.get('is_video', False),
                'hashtags': hashtags,
                'scraped_method': 'json_extraction'
            }
            
            return post
            
        except Exception as e:
            print(f"Error formatting post: {e}")
            return None

def test_scraper_v3():
    """Test the simple Instagram scraper"""
    scraper = InstagramScraperV3()
    
    username = 'example_user'
    
    print("=" * 60)
    print(f"Testing Simple Instagram Scraper with @{username}")
    print("=" * 60)
    
    posts = scraper.get_user_posts_simple(username, max_posts=5)
    
    if posts:
        print(f"\n🎉 Successfully found {len(posts)} posts!")
        
        for i, post in enumerate(posts, 1):
            print(f"\n📸 Post {i}:")
            print(f"  Method: {post.get('scraped_method', 'unknown')}")
            print(f"  Caption: {post['caption'][:80]}...")
            print(f"  Image URL: {post['image_url'][:60]}...")
            print(f"  Post URL: {post['post_url']}")
            if post.get('hashtags'):
                print(f"  Hashtags: {', '.join(post['hashtags'][:3])}")
        
        # Save results
        with open('scraped_posts_v3.json', 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved results to scraped_posts_v3.json")
        
        return posts
    else:
        print("\n❌ No posts found with any method")
        return []

if __name__ == "__main__":
    test_scraper_v3()