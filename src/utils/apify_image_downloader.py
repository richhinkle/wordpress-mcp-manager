"""
Apify-based Instagram image downloader
Uses Apify's Instagram Post Scraper and image download capabilities
"""

import requests
import json
import time
import base64
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ApifyImageDownloader:
    """
    Download Instagram images using Apify's specialized actors
    """
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.apify.com/v2"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        })
        
        # Actor IDs for image downloading
        self.instagram_scraper_id = "shu8hvrXbJbY3Eb9W"  # Working Instagram Scraper
        self.instagram_post_scraper_id = "nH2AHrwxeTRJoN5hX"  # Instagram Post Scraper
        
    def download_instagram_images_simple_approach(self, username: str, limit: int = 10) -> Dict:
        """
        Use Instagram Scraper + Web Scraper to download images
        Leverages Apify's ability to access Instagram images (as shown in their UI)
        
        Args:
            username: Instagram username (without @)
            limit: Number of posts to scrape
            
        Returns:
            Dictionary with download results and image data
        """
        try:
            logger.info(f"🔄 Starting Web Scraper image download for @{username}")
            
            # Step 1: Use Instagram Post Scraper to get post data and image URLs
            logger.info("📱 Step 1: Running Instagram Post Scraper...")
            scraper_input = {
                "usernames": [username],
                "resultsLimit": limit
            }
            
            scraper_run_response = self._start_actor_run(self.instagram_post_scraper_id, scraper_input)
            scraper_run_id = scraper_run_response['data']['id']
            
            # Wait for scraper to complete
            scraper_results = self._wait_for_completion(scraper_run_id)
            
            if not scraper_results:
                return {
                    'success': False,
                    'error': 'No posts found by Instagram Scraper'
                }
            
            logger.info(f"✅ Instagram Post Scraper found {len(scraper_results)} posts")
            
            # Step 2: Download images from Apify's CDN
            logger.info("🔍 Step 2: Downloading images from Apify CDN...")
            
            combined_results = []
            for i, post in enumerate(scraper_results):
                result_item = {
                    'post_data': post,
                    'image_url': post.get('displayUrl', ''),
                    'image_base64': None,
                    'download_success': False,
                    'download_error': None
                }
                
                # Log what we found
                logger.info(f"Post {i+1}: {post.get('shortCode', 'unknown')}")
                logger.info(f"  Image URL: {post.get('displayUrl', 'None')}")
                logger.info(f"  Caption: {post.get('caption', 'None')[:50]}...")
                
                # Try to download from Apify's CDN
                if post.get('displayUrl'):
                    display_url = post['displayUrl']
                    
                    # Check if it's an Apify CDN URL (these should be accessible)
                    if 'cdn-cms.apify.com' in display_url or 'apifyusercontent.com' in display_url:
                        logger.info(f"  🎯 Apify CDN URL detected - attempting download...")
                        
                        try:
                            # Download directly from Apify's CDN
                            response = requests.get(display_url, timeout=30)
                            response.raise_for_status()
                            
                            # Convert to base64
                            image_data = base64.b64encode(response.content).decode('utf-8')
                            
                            result_item['image_base64'] = image_data
                            result_item['download_success'] = True
                            result_item['image_size'] = len(response.content)
                            result_item['content_type'] = response.headers.get('content-type', 'image/jpeg')
                            
                            logger.info(f"  ✅ Downloaded {len(response.content)} bytes from Apify CDN")
                            
                        except Exception as e:
                            result_item['download_error'] = f"Apify CDN download failed: {str(e)}"
                            logger.warning(f"  ❌ Apify CDN download failed: {e}")
                    
                    else:
                        # Still an Instagram URL - can't download directly
                        result_item['download_error'] = "Instagram CDN URL - not downloadable"
                        logger.warning(f"  ⚠️ Instagram CDN URL (not Apify) - skipping download")
                        
                else:
                    result_item['download_error'] = "No image URL found"
                    logger.warning(f"  ❌ No image URL")
                
                combined_results.append(result_item)
            
            successful_downloads = sum(1 for r in combined_results if r['download_success'])
            
            return {
                'success': True,
                'method': 'apify_post_scraper_with_cdn_download',
                'username': username,
                'total_posts': len(scraper_results),
                'images_downloaded': successful_downloads,
                'images_available': sum(1 for r in combined_results if r['image_url']),
                'results': combined_results,
                'scraper_run_id': scraper_run_id
            }
            
        except Exception as e:
            logger.error(f"❌ Web Scraper image download failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'method': 'apify_web_scraper'
            }
    
    def download_instagram_images_method2(self, post_urls: List[str]) -> Dict:
        """
        Method 2: Direct Instagram Post Downloader for specific URLs
        
        Args:
            post_urls: List of Instagram post URLs
            
        Returns:
            Dictionary with download results
        """
        try:
            logger.info(f"🔄 Starting Method 2 image download for {len(post_urls)} URLs")
            
            # Use the general Instagram Scraper with direct URLs
            actor_input = {
                "directUrls": post_urls,
                "resultsType": "posts",
                "addParentData": False,
                "enhanceUserSearchWithFacebookPage": False
            }
            
            run_response = self._start_actor_run("apify/instagram-scraper", actor_input)
            run_id = run_response['data']['id']
            
            logger.info(f"📱 Instagram Scraper started for URLs, run ID: {run_id}")
            
            # Wait for completion
            results = self._wait_for_completion(run_id)
            
            # Process results and download images
            processed_results = []
            for item in results:
                if item.get('displayUrl'):
                    # Try to download the image directly through Apify's infrastructure
                    image_data = self._download_image_via_apify(item['displayUrl'])
                    
                    processed_results.append({
                        'post_data': item,
                        'image_url': item['displayUrl'],
                        'image_base64': image_data,
                        'download_success': image_data is not None
                    })
            
            return {
                'success': True,
                'method': 'apify_direct_url_scraper',
                'total_posts': len(results),
                'images_downloaded': sum(1 for r in processed_results if r['download_success']),
                'results': processed_results,
                'run_id': run_id
            }
            
        except Exception as e:
            logger.error(f"❌ Method 2 image download failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'method': 'apify_direct_url_scraper'
            }
    
    def _download_image_via_apify(self, image_url: str) -> Optional[str]:
        """
        Download a single image using Apify's Web Scraper with browser automation
        
        Args:
            image_url: Instagram image URL
            
        Returns:
            Base64 encoded image data or None if failed
        """
        try:
            # Use Apify's Web Scraper to download the image through browser automation
            web_scraper_input = {
                "startUrls": [{"url": image_url}],
                "pageFunction": """
                    async function pageFunction(context) {
                        const { page, request } = context;
                        
                        try {
                            // Navigate to the image URL
                            const response = await page.goto(request.url, { waitUntil: 'networkidle' });
                            
                            if (response && response.ok()) {
                                // Get the image as buffer
                                const buffer = await response.buffer();
                                
                                // Convert to base64
                                const base64 = buffer.toString('base64');
                                
                                return {
                                    url: request.url,
                                    success: true,
                                    imageData: base64,
                                    contentType: response.headers()['content-type'] || 'image/jpeg'
                                };
                            } else {
                                return {
                                    url: request.url,
                                    success: false,
                                    error: 'Failed to load image'
                                };
                            }
                        } catch (error) {
                            return {
                                url: request.url,
                                success: false,
                                error: error.message
                            };
                        }
                    }
                """,
                "maxRequestsPerCrawl": 1,
                "maxConcurrency": 1
            }
            
            run_response = self._start_actor_run("apify/web-scraper", web_scraper_input)
            run_id = run_response['data']['id']
            
            results = self._wait_for_completion(run_id, timeout=60)  # Shorter timeout for single image
            
            if results and len(results) > 0 and results[0].get('success'):
                return results[0].get('imageData')
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to download image via Apify Web Scraper: {e}")
            return None
    
    def save_base64_images_to_cache(self, results: List[Dict], cache_dir: Path) -> List[Dict]:
        """
        Save base64 image data to local cache files
        
        Args:
            results: List of result dictionaries with image_base64 data
            cache_dir: Directory to save cached images
            
        Returns:
            Updated results with cache_path information
        """
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        for result in results:
            if result.get('image_base64') and result.get('download_success'):
                try:
                    # Generate filename from post data
                    post_data = result.get('post_data', {})
                    shortcode = post_data.get('shortCode', post_data.get('shortcode', ''))
                    username = post_data.get('ownerUsername', post_data.get('username', 'unknown'))
                    
                    if shortcode:
                        filename = f"instagram_{username}_{shortcode}.jpg"
                    else:
                        # Use timestamp as fallback
                        import hashlib
                        hash_id = hashlib.md5(str(post_data).encode()).hexdigest()[:8]
                        filename = f"instagram_{username}_{hash_id}.jpg"
                    
                    cache_path = cache_dir / filename
                    
                    # Decode and save base64 image
                    image_data = base64.b64decode(result['image_base64'])
                    
                    with open(cache_path, 'wb') as f:
                        f.write(image_data)
                    
                    result['cache_path'] = cache_path
                    result['cache_filename'] = filename
                    result['cache_size_bytes'] = len(image_data)
                    
                    logger.info(f"💾 Cached image: {filename} ({len(image_data)} bytes)")
                    
                except Exception as e:
                    logger.error(f"Failed to cache image: {e}")
                    result['cache_error'] = str(e)
        
        return results
    
    def _start_actor_run(self, actor_id: str, actor_input: Dict) -> Dict:
        """Start an Apify actor run"""
        url = f"{self.base_url}/acts/{actor_id}/runs"
        
        response = self.session.post(url, json=actor_input)
        response.raise_for_status()
        
        return response.json()
    
    def _wait_for_completion(self, run_id: str, timeout: int = 300) -> List[Dict]:
        """Wait for actor run to complete and return results"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check run status
            status_url = f"{self.base_url}/actor-runs/{run_id}"
            status_response = self.session.get(status_url)
            status_response.raise_for_status()
            
            run_data = status_response.json()['data']
            status = run_data['status']
            
            logger.info(f"🔄 Run {run_id} status: {status}")
            
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
    
    def _get_images_from_kvs(self, kvs_id: str) -> List[Optional[str]]:
        """
        Get images from key-value store
        
        Args:
            kvs_id: Key-value store ID
            
        Returns:
            List of base64 encoded images
        """
        try:
            # Get the images-archive record from key-value store
            kvs_url = f"{self.base_url}/key-value-stores/{kvs_id}/records/images-archive"
            
            response = self.session.get(kvs_url)
            
            if response.status_code == 200:
                # The response should contain the images archive
                # This could be a ZIP file or JSON with base64 images
                content_type = response.headers.get('content-type', '')
                
                if 'application/json' in content_type:
                    # JSON format with base64 images
                    images_data = response.json()
                    if isinstance(images_data, list):
                        return images_data
                    elif isinstance(images_data, dict) and 'images' in images_data:
                        return images_data['images']
                
                elif 'application/zip' in content_type:
                    # ZIP archive - we'd need to extract and process
                    logger.info("📦 Received ZIP archive from key-value store")
                    # For now, return empty list - would need ZIP processing
                    return []
                
                else:
                    # Try to treat as base64 image data
                    try:
                        # If it's a single image, wrap in list
                        image_data = base64.b64encode(response.content).decode('utf-8')
                        return [image_data]
                    except:
                        return []
            
            else:
                logger.warning(f"⚠️ Key-value store request failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error retrieving images from key-value store: {e}")
            return []

def test_apify_image_downloader():
    """Test the Apify image downloader"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_token = os.getenv('APIFY_API_TOKEN')
    if not api_token:
        print("❌ APIFY_API_TOKEN not found")
        return
    
    downloader = ApifyImageDownloader(api_token)
    
    print("🧪 Testing Apify Image Downloader")
    print("=" * 50)
    
    # Test Simple Approach: Instagram Post Scraper Analysis
    print("\n📱 Testing Simple Approach: Instagram Post Scraper Analysis")
    result1 = downloader.download_instagram_images_simple_approach('example_user', limit=2)
    
    if result1['success']:
        print(f"✅ Success: {result1['images_downloaded']}/{result1['total_posts']} images downloaded")
        print(f"📊 Available URLs: {result1['images_available']}")
        print(f"🔗 Scraper Run ID: {result1.get('scraper_run_id')}")
        
        # Show details of posts
        for i, result in enumerate(result1['results']):
            if result['download_success']:
                size_kb = result.get('image_size', 0) / 1024
                print(f"   ✅ Post {i+1}: Downloaded {size_kb:.1f} KB ({result.get('content_type', 'unknown')})")
                print(f"      URL: {result['image_url']}")
            elif result['image_url']:
                error = result.get('download_error', 'Unknown error')
                print(f"   ⚠️ Post {i+1}: {error}")
                print(f"      URL: {result['image_url']}")
            else:
                print(f"   ❌ Post {i+1}: No image URL found")
        
        # Save successful downloads to cache
        if result1['images_downloaded'] > 0:
            cache_dir = Path("cache/apify_images")
            results_with_cache = downloader.save_base64_images_to_cache(result1['results'], cache_dir)
            
            cached_count = sum(1 for r in results_with_cache if r.get('cache_path'))
            print(f"💾 Cached {cached_count} images to {cache_dir}")
        
    else:
        print(f"❌ Failed: {result1['error']}")

if __name__ == "__main__":
    test_apify_image_downloader()