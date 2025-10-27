import requests
import json
import re
from urllib.parse import urljoin
import time
from typing import List, Dict, Optional

class InstagramScraper:
    def __init__(self):
        self.session = requests.Session()
        # Use a realistic user agent to avoid detection
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def get_user_posts(self, username: str, max_posts: int = 12) -> List[Dict]:
        """
        Scrape Instagram posts for a given username
        Returns list of post dictionaries with image URLs, captions, etc.
        """
        try:
            # Get the user's Instagram page
            url = f"https://www.instagram.com/{username}/"
            print(f"Fetching Instagram page: {url}")
            
            response = self.session.get(url)
            response.raise_for_status()
            
            # Extract JSON data from the page
            posts_data = self._extract_posts_from_html(response.text)
            
            if not posts_data:
                print("No posts data found")
                return []
            
            # Process and format the posts
            formatted_posts = []
            for i, post in enumerate(posts_data[:max_posts]):
                formatted_post = self._format_post_data(post, username)
                if formatted_post:
                    formatted_posts.append(formatted_post)
                    print(f"Processed post {i+1}: {formatted_post.get('caption', '')[:50]}...")
            
            print(f"Successfully scraped {len(formatted_posts)} posts from @{username}")
            return formatted_posts
            
        except requests.RequestException as e:
            print(f"Error fetching Instagram page: {e}")
            return []
        except Exception as e:
            print(f"Error processing Instagram data: {e}")
            return []
    
    def _extract_posts_from_html(self, html: str) -> List[Dict]:
        """Extract posts data from Instagram HTML page"""
        try:
            # Look for the JSON data in script tags
            # Instagram embeds data in window._sharedData
            pattern = r'window\._sharedData\s*=\s*({.*?});'
            match = re.search(pattern, html)
            
            if match:
                json_data = json.loads(match.group(1))
                
                # Navigate through the JSON structure to find posts
                entry_data = json_data.get('entry_data', {})
                profile_page = entry_data.get('ProfilePage', [])
                
                if profile_page:
                    user_data = profile_page[0].get('graphql', {}).get('user', {})
                    timeline_media = user_data.get('edge_owner_to_timeline_media', {})
                    edges = timeline_media.get('edges', [])
                    
                    return [edge.get('node', {}) for edge in edges]
            
            # Fallback: try to find JSON-LD data or other embedded JSON
            json_pattern = r'<script type="application/ld\+json">(.*?)</script>'
            json_matches = re.findall(json_pattern, html, re.DOTALL)
            
            for json_match in json_matches:
                try:
                    data = json.loads(json_match)
                    # Process JSON-LD data if it contains posts
                    if isinstance(data, dict) and 'mainEntity' in data:
                        # Handle structured data format
                        pass
                except json.JSONDecodeError:
                    continue
            
            print("Could not find posts data in HTML")
            return []
            
        except Exception as e:
            print(f"Error extracting posts from HTML: {e}")
            return []
    
    def _format_post_data(self, post_node: Dict, username: str) -> Optional[Dict]:
        """Format raw Instagram post data into a clean structure"""
        try:
            # Extract basic post information
            post_id = post_node.get('id', '')
            shortcode = post_node.get('shortcode', '')
            
            # Get image URL (highest quality available)
            display_url = post_node.get('display_url', '')
            
            # Get caption
            caption_edges = post_node.get('edge_media_to_caption', {}).get('edges', [])
            caption = ''
            if caption_edges:
                caption = caption_edges[0].get('node', {}).get('text', '')
            
            # Get timestamp
            timestamp = post_node.get('taken_at_timestamp', 0)
            
            # Get engagement metrics
            likes = post_node.get('edge_media_preview_like', {}).get('count', 0)
            comments = post_node.get('edge_media_to_comment', {}).get('count', 0)
            
            # Check if it's a video
            is_video = post_node.get('is_video', False)
            
            # Extract hashtags from caption
            hashtags = re.findall(r'#(\w+)', caption) if caption else []
            
            formatted_post = {
                'id': post_id,
                'shortcode': shortcode,
                'username': username,
                'caption': caption,
                'image_url': display_url,
                'post_url': f"https://www.instagram.com/p/{shortcode}/",
                'timestamp': timestamp,
                'likes': likes,
                'comments': comments,
                'is_video': is_video,
                'hashtags': hashtags
            }
            
            return formatted_post
            
        except Exception as e:
            print(f"Error formatting post data: {e}")
            return None

def test_scraper():
    """Test the Instagram scraper with example_user"""
    scraper = InstagramScraper()
    
    print("Testing Instagram scraper with example_user...")
    posts = scraper.get_user_posts('example_user', max_posts=5)
    
    if posts:
        print(f"\n✅ Successfully scraped {len(posts)} posts!")
        for i, post in enumerate(posts, 1):
            print(f"\nPost {i}:")
            print(f"  Caption: {post['caption'][:100]}...")
            print(f"  Image URL: {post['image_url']}")
            print(f"  Likes: {post['likes']}")
            print(f"  Hashtags: {post['hashtags'][:5]}")  # First 5 hashtags
    else:
        print("❌ No posts found or scraping failed")

if __name__ == "__main__":
    test_scraper()