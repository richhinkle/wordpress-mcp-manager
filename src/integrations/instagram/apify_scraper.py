"""
Apify Instagram Scraper Integration
Professional Instagram scraping using Apify's Instagram Scraper actor
"""

import requests
import json
import time
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ApifyInstagramScraper:
    """
    Professional Instagram scraper using Apify's Instagram Scraper actor
    Handles rate limiting, data formatting, and error handling
    """
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.apify.com/v2"
        self.actor_id = "shu8hvrXbJbY3Eb9W"  # Instagram Scraper actor ID from Apify example
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        })
    
    def scrape_user_posts(self, username: str, limit: int = 50, include_stories: bool = False) -> List[Dict]:
        """
        Scrape posts from an Instagram user
        
        Args:
            username: Instagram username (without @)
            limit: Maximum number of posts to scrape
            include_stories: Whether to include stories (premium feature)
            
        Returns:
            List of formatted post dictionaries
        """
        logger.info(f"Starting Apify scrape for @{username}, limit: {limit}")
        
        # Prepare input for Apify actor (based on successful console run)
        actor_input = {
            "addParentData": False,
            "directUrls": [f"https://www.instagram.com/{username}/"],
            "enhanceUserSearchWithFacebookPage": False,
            "isUserReelFeedURL": False,
            "isUserTaggedFeedURL": False,
            "onlyPostsNewerThan": "2024-01-01",  # Get posts from this year
            "resultsLimit": limit,
            "resultsType": "posts",
            "searchLimit": 1,
            "searchType": "hashtag"
        }
        
        try:
            # Start the actor run
            run_response = self._start_actor_run(actor_input)
            run_id = run_response['data']['id']
            
            logger.info(f"Apify run started with ID: {run_id}")
            
            # Wait for completion and get results
            results = self._wait_for_completion(run_id)
            
            # Debug: Log what we actually received
            logger.info(f"Received {len(results)} items from Apify for @{username}")
            if results:
                logger.info(f"First item keys: {list(results[0].keys()) if results[0] else 'Empty item'}")
                logger.info(f"First item type: {results[0].get('type') if results[0] else 'No type'}")
                logger.info(f"Sample data: {str(results[0])[:300]}...")
            
            # Format results for WordPress import
            formatted_posts = []
            for item in results:
                # Check for Instagram posts (Apify uses 'Image' or 'Video' as type)
                if item.get('type') in ['Image', 'Video'] or 'shortCode' in item:
                    formatted_post = self._format_post_data(item, username)
                    if formatted_post:
                        formatted_posts.append(formatted_post)
            
            logger.info(f"Successfully scraped {len(formatted_posts)} posts from @{username}")
            return formatted_posts
            
        except Exception as e:
            logger.error(f"Error scraping @{username}: {str(e)}")
            raise
    
    def scrape_post_urls(self, urls: List[str]) -> List[Dict]:
        """
        Scrape specific Instagram posts by URL
        
        Args:
            urls: List of Instagram post URLs
            
        Returns:
            List of formatted post dictionaries
        """
        logger.info(f"Starting Apify scrape for {len(urls)} specific URLs")
        
        # Prepare input for URL-based scraping
        actor_input = {
            "addParentData": False,
            "directUrls": urls,
            "enhanceUserSearchWithFacebookPage": False,
            "isUserReelFeedURL": False,
            "isUserTaggedFeedURL": False,
            "onlyPostsNewerThan": "2024-01-01",
            "resultsLimit": len(urls) * 10,  # Allow multiple posts per URL
            "resultsType": "posts",
            "searchLimit": 1,
            "searchType": "hashtag"
        }
        
        try:
            # Start the actor run
            run_response = self._start_actor_run(actor_input)
            run_id = run_response['data']['id']
            
            logger.info(f"Apify URL scrape started with ID: {run_id}")
            
            # Wait for completion and get results
            results = self._wait_for_completion(run_id)
            
            # Format results
            formatted_posts = []
            for item in results:
                if item.get('type') == 'post':
                    # Extract username from URL or use 'unknown'
                    username = self._extract_username_from_url(item.get('url', ''))
                    formatted_post = self._format_post_data(item, username)
                    if formatted_post:
                        formatted_posts.append(formatted_post)
            
            logger.info(f"Successfully scraped {len(formatted_posts)} posts from URLs")
            return formatted_posts
            
        except Exception as e:
            logger.error(f"Error scraping URLs: {str(e)}")
            raise
    
    def get_user_profile(self, username: str) -> Dict:
        """
        Get Instagram user profile information
        
        Args:
            username: Instagram username (without @)
            
        Returns:
            User profile dictionary
        """
        logger.info(f"Getting profile info for @{username}")
        
        actor_input = {
            "addParentData": False,
            "directUrls": [f"https://www.instagram.com/{username}/"],
            "enhanceUserSearchWithFacebookPage": False,
            "isUserReelFeedURL": False,
            "isUserTaggedFeedURL": False,
            "resultsLimit": 1,
            "resultsType": "details",
            "searchLimit": 1,
            "searchType": "hashtag"
        }
        
        try:
            run_response = self._start_actor_run(actor_input)
            run_id = run_response['data']['id']
            
            results = self._wait_for_completion(run_id)
            
            # Debug: Log what we actually received
            logger.info(f"Received {len(results)} items from Apify for profile @{username}")
            if results:
                logger.info(f"First item keys: {list(results[0].keys()) if results[0] else 'Empty item'}")
                logger.info(f"First item sample: {str(results[0])[:500]}...")
            
            # Find user profile in results
            for item in results:
                if item.get('type') == 'user' and item.get('username') == username:
                    return {
                        'username': item.get('username'),
                        'full_name': item.get('fullName'),
                        'biography': item.get('biography'),
                        'followers_count': item.get('followersCount'),
                        'following_count': item.get('followingCount'),
                        'posts_count': item.get('postsCount'),
                        'profile_pic_url': item.get('profilePicUrl'),
                        'is_verified': item.get('verified', False),
                        'is_private': item.get('private', False)
                    }
            
            logger.warning(f"Profile not found for @{username}")
            return {}
            
        except Exception as e:
            logger.error(f"Error getting profile for @{username}: {str(e)}")
            raise
    
    def _start_actor_run(self, actor_input: Dict) -> Dict:
        """Start an Apify actor run"""
        url = f"{self.base_url}/acts/{self.actor_id}/runs"
        
        response = self.session.post(url, json=actor_input)
        response.raise_for_status()
        
        return response.json()
    
    def _wait_for_completion(self, run_id: str, timeout: int = 300) -> List[Dict]:
        """
        Wait for actor run to complete and return results
        
        Args:
            run_id: Apify run ID
            timeout: Maximum wait time in seconds
            
        Returns:
            List of scraped items
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check run status
            status_url = f"{self.base_url}/actor-runs/{run_id}"
            status_response = self.session.get(status_url)
            status_response.raise_for_status()
            
            run_data = status_response.json()['data']
            status = run_data['status']
            
            logger.info(f"Run {run_id} status: {status}")
            
            if status == 'SUCCEEDED':
                # Get results
                results_url = f"{self.base_url}/actor-runs/{run_id}/dataset/items"
                results_response = self.session.get(results_url)
                results_response.raise_for_status()
                
                return results_response.json()
            
            elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                error_msg = f"Actor run {status.lower()}: {run_data.get('statusMessage', 'Unknown error')}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Wait before checking again
            time.sleep(10)
        
        raise Exception(f"Actor run timed out after {timeout} seconds")
    
    def _format_post_data(self, item: Dict, username: str) -> Optional[Dict]:
        """
        Format Apify result into our standard post format
        
        Args:
            item: Raw Apify result item
            username: Instagram username
            
        Returns:
            Formatted post dictionary or None if invalid
        """
        try:
            # Extract basic post data (based on actual Apify output format)
            post_id = item.get('id', '')
            shortcode = item.get('shortCode', '')  # Note: Apify uses 'shortCode' not 'shortcode'
            caption = item.get('caption', '')
            
            # Get the image URL (Apify provides displayUrl directly)
            image_url = item.get('displayUrl', '')
            
            # Handle video posts
            is_video = item.get('type', '').lower() == 'video'
            if is_video and item.get('videoUrl'):
                # For videos, we might want to use the video URL or thumbnail
                # For now, we'll use displayUrl as thumbnail and note it's a video
                pass
            
            # Parse timestamp (Apify format: "2025-10-20T14:54:06.000Z")
            timestamp = 0
            date_posted = ''
            if item.get('timestamp'):
                try:
                    # Apify returns timestamp in ISO format
                    dt = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
                    timestamp = int(dt.timestamp())
                    date_posted = dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    logger.warning(f"Error parsing timestamp {item.get('timestamp')}: {e}")
                    timestamp = int(time.time())
                    date_posted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Extract hashtags (Apify provides them directly in the hashtags array)
            hashtags = item.get('hashtags', [])
            
            # Build post URL (Apify provides this directly)
            post_url = item.get('url', '')
            
            # Get owner information
            owner_username = item.get('ownerUsername', username)
            owner_full_name = item.get('ownerFullName', '')
            
            formatted_post = {
                'id': post_id,
                'shortcode': shortcode,
                'username': owner_username,
                'caption': caption,
                'image_url': image_url,
                'post_url': post_url,
                'timestamp': timestamp,
                'date_posted': date_posted,
                'hashtags': hashtags,
                'media_type': item.get('type', 'Image').upper(),
                'is_video': is_video,
                'likes_count': item.get('likesCount', 0),
                'comments_count': item.get('commentsCount', 0),
                'owner_full_name': owner_full_name,
                'dimensions_height': item.get('dimensionsHeight', 0),
                'dimensions_width': item.get('dimensionsWidth', 0),
                'location_name': item.get('locationName', ''),
                'alt_text': item.get('alt', ''),
                'extraction_method': 'apify_scraper',
                'raw_data': item  # Store original data for debugging
            }
            
            # Add video-specific data if it's a video
            if is_video:
                formatted_post.update({
                    'video_url': item.get('videoUrl', ''),
                    'video_view_count': item.get('videoViewCount', 0),
                    'video_play_count': item.get('videoPlayCount', 0),
                    'video_duration': item.get('videoDuration', 0)
                })
            
            return formatted_post
            
        except Exception as e:
            logger.error(f"Error formatting post data: {str(e)}")
            logger.error(f"Item data: {str(item)[:500]}...")
            return None
    
    def _extract_username_from_url(self, url: str) -> str:
        """Extract username from Instagram URL"""
        try:
            import re
            match = re.search(r'instagram\.com/([^/]+)/', url)
            return match.group(1) if match else 'unknown'
        except:
            return 'unknown'
    
    def get_usage_info(self) -> Dict:
        """
        Get current Apify account usage information
        
        Returns:
            Usage statistics dictionary
        """
        try:
            url = f"{self.base_url}/users/me"
            response = self.session.get(url)
            response.raise_for_status()
            
            user_data = response.json()['data']
            
            return {
                'monthly_usage': user_data.get('monthlyUsage', {}),
                'limits': user_data.get('limits', {}),
                'plan': user_data.get('plan', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Error getting usage info: {str(e)}")
            return {}
    
    def find_instagram_actors(self) -> List[Dict]:
        """
        Find available Instagram-related actors
        
        Returns:
            List of actor information
        """
        try:
            url = f"{self.base_url}/store"
            params = {
                'search': 'instagram',
                'category': 'SOCIAL_MEDIA'
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            actors = data.get('data', {}).get('items', [])
            
            instagram_actors = []
            for actor in actors:
                if 'instagram' in actor.get('name', '').lower():
                    instagram_actors.append({
                        'id': actor.get('id'),
                        'name': actor.get('name'),
                        'username': actor.get('username'),
                        'title': actor.get('title'),
                        'description': actor.get('description', '')[:100]
                    })
            
            return instagram_actors
            
        except Exception as e:
            logger.error(f"Error finding Instagram actors: {str(e)}")
            return []
    
    def test_actor_availability(self, actor_id: str) -> bool:
        """
        Test if an actor ID is available and accessible
        
        Args:
            actor_id: Actor ID to test
            
        Returns:
            True if actor is available, False otherwise
        """
        try:
            url = f"{self.base_url}/acts/{actor_id}"
            response = self.session.get(url)
            return response.status_code == 200
        except:
            return False

class ApifyInstagramManager:
    """
    High-level manager for Apify Instagram integration with WordPress
    Combines scraping and WordPress import functionality
    """
    
    def __init__(self, api_token: str, mcp_client, cache_ttl: int = 3600):
        from .apify_cache import CachedApifyInstagramScraper
        
        self.scraper = CachedApifyInstagramScraper(api_token, cache_ttl)
        self.mcp_client = mcp_client
        logger.info("ApifyInstagramManager initialized with caching")
    
    def import_user_posts_to_wordpress(self, username: str, limit: int = 10, auto_publish: bool = False, progress_session_id: str = None) -> Dict:
        """
        Scrape user posts via Apify and import directly to WordPress
        
        Args:
            username: Instagram username (without @)
            limit: Maximum number of posts to import
            auto_publish: Whether to publish posts immediately (vs draft)
            
        Returns:
            Import results dictionary
        """
        try:
            logger.info(f"Starting bulk import for @{username}, limit: {limit}")
            
            # Import progress tracking functions
            if progress_session_id:
                try:
                    from ...api.progress_routes import update_progress
                    update_progress(progress_session_id, step=5, message=f"🔍 Scraping @{username} via Apify...")
                except ImportError:
                    pass
            
            # Step 1: Scrape posts
            posts = self.scraper.scrape_user_posts(username, limit)
            
            if progress_session_id:
                try:
                    update_progress(progress_session_id, step=20, message=f"📱 Found {len(posts)} posts, starting import...")
                except:
                    pass
            
            if not posts:
                return {
                    'success': False,
                    'message': f'No posts found for @{username}',
                    'scraped_count': 0,
                    'imported_count': 0
                }
            
            # Step 2: Import to WordPress
            imported_posts = []
            total_posts = len(posts)
            
            for i, post in enumerate(posts, 1):
                try:
                    # Download and upload image to WordPress using proven breakthrough method
                    media_id = None
                    if post.get('image_url'):
                        try:
                            # Use the proven working Instagram image downloader
                            from ...utils.instagram_image_downloader_working import InstagramImageDownloader
                            
                            downloader = InstagramImageDownloader()
                            success, image_data, error = downloader.download_image(post['image_url'])
                            
                            if success and image_data:
                                logger.info(f"✅ Downloaded {len(image_data)} bytes for post {post.get('shortcode')}")
                                
                                # Upload to WordPress using REST API
                                wp_url = self.mcp_client.wordpress_url.replace('/wp-json/mcp/v1/sse', '')
                                upload_url = f"{wp_url}/wp-json/wp/v2/media"
                                
                                # Use WordPress credentials from environment
                                import os
                                wp_username = os.getenv('WORDPRESS_USERNAME', 'admin')
                                wp_password = os.getenv('WORDPRESS_PASSWORD', '')
                                
                                if wp_username and wp_password:
                                    import base64
                                    credentials = base64.b64encode(f"{wp_username}:{wp_password}".encode()).decode()
                                    
                                    filename = f"instagram_{post.get('username', 'unknown')}_{post.get('shortcode', 'unknown')}.jpg"
                                    
                                    files = {
                                        'file': (filename, image_data, 'image/jpeg')
                                    }
                                    
                                    upload_headers = {
                                        'Authorization': f'Basic {credentials}'
                                    }
                                    
                                    upload_response = requests.post(upload_url, files=files, headers=upload_headers, timeout=60)
                                    
                                    if upload_response.status_code == 201:
                                        media_data = upload_response.json()
                                        media_id = media_data['id']
                                        logger.info(f"✅ Successfully uploaded image for post {post.get('shortcode')} (Media ID: {media_id})")
                                    else:
                                        logger.warning(f"⚠️ WordPress upload failed: {upload_response.status_code} - {upload_response.text[:200]}")
                                else:
                                    logger.warning("⚠️ WordPress credentials not configured for direct upload")
                            else:
                                logger.warning(f"⚠️ Image download failed for post {post.get('shortcode')}: {error}")
                            
                        except Exception as e:
                            logger.warning(f"⚠️ Image download/upload failed for post {post.get('shortcode')}: {e}")
                            # Fall back to MCP upload (will likely fail but worth trying)
                            try:
                                media_result = self.mcp_client.upload_media(
                                    url=post['image_url'],
                                    title=f"Instagram - @{username} - {post.get('caption', '')[:50]}",
                                    alt=post.get('caption', '')[:100]
                                )
                                if media_result and 'id' in media_result:
                                    media_id = media_result['id']
                            except:
                                pass
                    
                    # Create post title
                    post_title = f"@{username} - {datetime.now().strftime('%Y-%m-%d')}"
                    if post.get('caption'):
                        first_line = post['caption'].split('\n')[0][:50]
                        if first_line and not first_line.startswith('#'):
                            post_title = first_line
                    
                    # Enhanced content with beautiful Instagram-style formatting
                    content = self._format_instagram_post_content(post, username)
                    
                    # Create WordPress post
                    status = 'publish' if auto_publish else 'draft'
                    wp_result = self.mcp_client.create_post(
                        title=post_title,
                        content=content,
                        status=status
                    )
                    
                    # Parse post ID
                    post_id = None
                    if isinstance(wp_result, dict) and 'ID' in wp_result:
                        post_id = wp_result['ID']
                    elif isinstance(wp_result, str) and 'Post created ID' in wp_result:
                        import re
                        match = re.search(r'Post created ID (\d+)', wp_result)
                        if match:
                            post_id = int(match.group(1))
                    
                    # Add comprehensive metadata
                    if post_id:
                        meta_fields = {
                            'instagram_username': username,
                            'instagram_shortcode': post.get('shortcode', ''),
                            'instagram_likes': str(post.get('likes_count', 0)),
                            'instagram_comments': str(post.get('comments_count', 0)),
                            'instagram_hashtags': ','.join(post.get('hashtags', [])),
                            'instagram_post_url': post.get('post_url', ''),
                            'import_method': 'apify_bulk_import',
                            'import_date': datetime.now().isoformat()
                        }
                        
                        for key, value in meta_fields.items():
                            try:
                                self.mcp_client.call_mcp_function('wp_update_post_meta', {
                                    'ID': post_id,
                                    'key': key,
                                    'value': value
                                })
                            except Exception as e:
                                logger.warning(f"Could not add meta field {key}: {e}")
                        
                        # Set featured image
                        if media_id:
                            try:
                                self.mcp_client.set_featured_image(post_id, media_id)
                            except Exception as e:
                                logger.warning(f"Could not set featured image: {e}")
                    
                    imported_posts.append({
                        'shortcode': post.get('shortcode'),
                        'wordpress_id': post_id,
                        'title': post_title,
                        'status': status
                    })
                    
                    # Update progress
                    if progress_session_id:
                        try:
                            progress_step = 20 + int((i / total_posts) * 70)  # 20-90% range for import
                            update_progress(
                                progress_session_id, 
                                step=progress_step, 
                                message=f"📝 Imported {len(imported_posts)} of {total_posts} posts...",
                                details={'imported': len(imported_posts), 'total': total_posts}
                            )
                        except:
                            pass
                    
                except Exception as e:
                    logger.error(f"Error importing post {post.get('shortcode')}: {e}")
                    
                    # Update progress even on error
                    if progress_session_id:
                        try:
                            progress_step = 20 + int((i / total_posts) * 70)
                            update_progress(
                                progress_session_id, 
                                step=progress_step, 
                                message=f"📝 Processing {i} of {total_posts} posts (some errors)...",
                                details={'imported': len(imported_posts), 'total': total_posts, 'errors': i - len(imported_posts)}
                            )
                        except:
                            pass
                    continue
            
            # Final progress update
            if progress_session_id:
                try:
                    from ...api.progress_routes import complete_progress
                    complete_progress(
                        progress_session_id, 
                        f"✅ Successfully imported {len(imported_posts)} of {len(posts)} posts from @{username}!"
                    )
                except:
                    pass
            
            return {
                'success': True,
                'username': username,
                'scraped_count': len(posts),
                'imported_count': len(imported_posts),
                'imported_posts': imported_posts,
                'message': f'Successfully imported {len(imported_posts)} of {len(posts)} posts from @{username}'
            }
            
        except Exception as e:
            logger.error(f"Error in bulk import for @{username}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'scraped_count': 0,
                'imported_count': 0
            }
    
    def _format_instagram_post_content(self, post, username):
        """
        Format Instagram post content with clean, readable styling
        """
        caption = post.get('caption', '').strip()
        hashtags = post.get('hashtags', [])
        likes_count = post.get('likes_count', 0)
        comments_count = post.get('comments_count', 0)
        date_posted = post.get('date_posted', 'Unknown')
        post_url = post.get('post_url', '')
        
        # Split caption and hashtags
        caption_lines = caption.split('\n')
        main_caption = []
        caption_hashtags = []
        
        for line in caption_lines:
            if line.strip().startswith('#') or all(word.startswith('#') for word in line.strip().split() if word):
                caption_hashtags.extend([word for word in line.split() if word.startswith('#')])
            else:
                main_caption.append(line)
        
        # Combine hashtags from caption and metadata
        all_hashtags = list(set(caption_hashtags + hashtags))
        
        # Build clean, readable content
        content_parts = []
        
        # Main caption (clean, without hashtags)
        clean_caption = '\n'.join(main_caption).strip()
        if clean_caption:
            content_parts.append(clean_caption)
        
        # Add hashtags as a clean list
        if all_hashtags:
            hashtag_text = ' '.join([f'#{tag.lstrip("#")}' for tag in all_hashtags[:10]])
            content_parts.append(f"\n🏷️ **Tags:** {hashtag_text}")
        
        # Add Instagram metadata in a clean format
        metadata_parts = [
            "---",
            f"📸 **Instagram Post by @{username}**",
            f"📅 **Posted:** {date_posted}",
            f"❤️ **{likes_count:,} likes** • 💬 **{comments_count:,} comments**",
            f"🔗 [**View Original on Instagram**]({post_url})",
            "---"
        ]
        
        content_parts.extend(metadata_parts)
        
        return '\n\n'.join(content_parts)

def test_apify_scraper():
    """Test function for Apify scraper (requires API token)"""
    import os
    
    api_token = os.getenv('APIFY_API_TOKEN')
    if not api_token:
        print("❌ APIFY_API_TOKEN not found in environment variables")
        print("Get your token from: https://console.apify.com/account/integrations")
        return
    
    scraper = ApifyInstagramScraper(api_token)
    
    print("=" * 60)
    print("Apify Instagram Scraper Test")
    print("=" * 60)
    
    try:
        # Test usage info
        print("\n📊 Account Usage Info:")
        usage = scraper.get_usage_info()
        if usage:
            print(f"Plan: {usage.get('plan', 'Unknown')}")
            monthly = usage.get('monthly_usage', {})
            if monthly:
                print(f"Monthly usage: {monthly}")
        
        # Test profile scraping
        print(f"\n👤 Getting profile info for @example_user...")
        profile = scraper.get_user_profile('example_user')
        if profile:
            print(f"✅ Profile found:")
            print(f"   Full name: {profile.get('full_name')}")
            print(f"   Followers: {profile.get('followers_count')}")
            print(f"   Posts: {profile.get('posts_count')}")
        
        # Test post scraping (small sample)
        print(f"\n📱 Scraping 3 recent posts from @example_user...")
        posts = scraper.scrape_user_posts('example_user', limit=3)
        
        print(f"✅ Scraped {len(posts)} posts:")
        for i, post in enumerate(posts, 1):
            print(f"\n   Post {i}:")
            print(f"   Caption: {post['caption'][:50]}...")
            print(f"   Likes: {post['likes_count']}")
            print(f"   Comments: {post['comments_count']}")
            print(f"   Hashtags: {post['hashtags'][:3]}")
            print(f"   Date: {post['date_posted']}")
        
        print(f"\n🎉 Apify scraper test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_apify_scraper()