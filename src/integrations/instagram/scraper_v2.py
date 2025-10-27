import instaloader
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class InstagramScraperV2:
    def __init__(self):
        # Create instaloader instance
        self.loader = instaloader.Instaloader(
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
        
        # Disable downloading to avoid creating files
        self.loader.download_pictures = False
    
    def get_user_posts(self, username: str, max_posts: int = 12) -> List[Dict]:
        """
        Get Instagram posts for a given username using instaloader
        Returns list of post dictionaries with image URLs, captions, etc.
        """
        try:
            print(f"Fetching posts from @{username}...")
            
            # Get the profile
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            print(f"Profile found: {profile.full_name} (@{profile.username})")
            print(f"Followers: {profile.followers}, Posts: {profile.mediacount}")
            
            posts = []
            post_count = 0
            
            # Iterate through posts
            for post in profile.get_posts():
                if post_count >= max_posts:
                    break
                
                try:
                    # Extract post data
                    post_data = self._extract_post_data(post, username)
                    if post_data:
                        posts.append(post_data)
                        print(f"✅ Post {post_count + 1}: {post_data['caption'][:50]}...")
                        post_count += 1
                
                except Exception as e:
                    print(f"❌ Error processing post: {e}")
                    continue
            
            print(f"\n🎉 Successfully scraped {len(posts)} posts from @{username}")
            return posts
            
        except instaloader.exceptions.ProfileNotExistsException:
            print(f"❌ Profile @{username} does not exist")
            return []
        except instaloader.exceptions.LoginRequiredException:
            print("❌ Login required - trying anonymous access")
            return []
        except Exception as e:
            print(f"❌ Error fetching posts: {e}")
            return []
    
    def _extract_post_data(self, post, username: str) -> Optional[Dict]:
        """Extract relevant data from an instaloader Post object"""
        try:
            # Basic post info
            post_data = {
                'id': post.mediaid,
                'shortcode': post.shortcode,
                'username': username,
                'caption': post.caption or '',
                'post_url': f"https://www.instagram.com/p/{post.shortcode}/",
                'timestamp': int(post.date_utc.timestamp()),
                'date_posted': post.date_utc.strftime('%Y-%m-%d %H:%M:%S'),
                'likes': post.likes,
                'comments': post.comments,
                'is_video': post.is_video,
            }
            
            # Get image URL
            if hasattr(post, 'url'):
                post_data['image_url'] = post.url
            else:
                post_data['image_url'] = ''
            
            # Extract hashtags from caption
            if post_data['caption']:
                import re
                hashtags = re.findall(r'#(\w+)', post_data['caption'])
                post_data['hashtags'] = hashtags
            else:
                post_data['hashtags'] = []
            
            # Handle carousel posts (multiple images)
            if hasattr(post, 'get_sidecar_nodes'):
                try:
                    sidecar_nodes = list(post.get_sidecar_nodes())
                    if sidecar_nodes:
                        post_data['is_carousel'] = True
                        post_data['carousel_images'] = []
                        for node in sidecar_nodes:
                            if hasattr(node, 'display_url'):
                                post_data['carousel_images'].append(node.display_url)
                        # Use first image as main image
                        if post_data['carousel_images']:
                            post_data['image_url'] = post_data['carousel_images'][0]
                except:
                    post_data['is_carousel'] = False
            else:
                post_data['is_carousel'] = False
            
            return post_data
            
        except Exception as e:
            print(f"Error extracting post data: {e}")
            return None
    
    def get_profile_info(self, username: str) -> Optional[Dict]:
        """Get basic profile information"""
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            return {
                'username': profile.username,
                'full_name': profile.full_name,
                'biography': profile.biography,
                'followers': profile.followers,
                'following': profile.followees,
                'posts_count': profile.mediacount,
                'profile_pic_url': profile.profile_pic_url,
                'is_verified': profile.is_verified,
                'is_private': profile.is_private
            }
        except Exception as e:
            print(f"Error getting profile info: {e}")
            return None

def test_scraper_v2():
    """Test the improved Instagram scraper"""
    scraper = InstagramScraperV2()
    
    username = 'example_user'
    
    print("=" * 60)
    print(f"Testing Instagram Scraper V2 with @{username}")
    print("=" * 60)
    
    # Get profile info first
    profile_info = scraper.get_profile_info(username)
    if profile_info:
        print(f"\n📋 Profile Info:")
        print(f"  Name: {profile_info['full_name']}")
        print(f"  Bio: {profile_info['biography'][:100]}...")
        print(f"  Followers: {profile_info['followers']}")
        print(f"  Posts: {profile_info['posts_count']}")
        print(f"  Private: {profile_info['is_private']}")
    
    # Get posts
    posts = scraper.get_user_posts(username, max_posts=5)
    
    if posts:
        print(f"\n📸 Posts Summary:")
        for i, post in enumerate(posts, 1):
            print(f"\n  Post {i}:")
            print(f"    Date: {post['date_posted']}")
            print(f"    Caption: {post['caption'][:80]}...")
            print(f"    Likes: {post['likes']}")
            print(f"    Comments: {post['comments']}")
            print(f"    Hashtags: {', '.join(post['hashtags'][:3])}")
            print(f"    Image URL: {post['image_url'][:60]}...")
            if post.get('is_carousel'):
                print(f"    Carousel: {len(post.get('carousel_images', []))} images")
        
        # Save to JSON for inspection
        with open('scraped_posts.json', 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved {len(posts)} posts to scraped_posts.json")
        
    else:
        print("\n❌ No posts found")

if __name__ == "__main__":
    test_scraper_v2()