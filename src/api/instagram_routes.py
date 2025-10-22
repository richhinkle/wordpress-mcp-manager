"""
Instagram API Routes for Apify Integration
Handles Apify-based Instagram scraping endpoints
"""

from flask import Blueprint, request, jsonify, session
import logging
from datetime import datetime
import os

# Import our integrations
from ..integrations.instagram.apify_scraper import ApifyInstagramScraper

logger = logging.getLogger(__name__)

# Create Blueprint for Instagram routes
instagram_bp = Blueprint('instagram', __name__, url_prefix='/api/instagram')

@instagram_bp.route('/apify/status')
def apify_status():
    """Check Apify integration status and account info"""
    from flask import current_app
    apify_manager = current_app.config.get('apify_manager')
    
    if not apify_manager:
        return jsonify({
            'available': False,
            'error': 'APIFY_API_TOKEN not configured'
        }), 400
    
    try:
        usage_info = apify_manager.scraper.get_usage_info()
        cache_stats = apify_manager.scraper.get_cache_stats()
        
        return jsonify({
            'available': True,
            'usage_info': usage_info,
            'cache_stats': cache_stats,
            'message': 'Apify integration ready with caching'
        })
    except Exception as e:
        return jsonify({
            'available': False,
            'error': str(e)
        }), 500

@instagram_bp.route('/apify/scrape-user', methods=['POST'])
def scrape_user_posts():
    """Scrape posts from Instagram user via Apify"""
    from flask import current_app
    apify_manager = current_app.config.get('apify_manager')
    
    if not apify_manager:
        return jsonify({'error': 'Apify not configured'}), 400
    
    try:
        data = request.json
        username = data.get('username', '').replace('@', '')
        limit = data.get('limit', 20)
        include_stories = data.get('include_stories', False)
        
        if not username:
            return jsonify({'error': 'Username is required'}), 400
        
        logger.info(f"Scraping @{username} via Apify, limit: {limit}")
        
        # Scrape posts using Apify
        posts = apify_manager.scraper.scrape_user_posts(
            username=username,
            limit=limit,
            include_stories=include_stories
        )
        
        return jsonify({
            'success': True,
            'username': username,
            'posts_count': len(posts),
            'posts': posts,
            'message': f'Successfully scraped {len(posts)} posts from @{username}'
        })
        
    except Exception as e:
        logger.error(f"Error scraping user posts: {str(e)}")
        return jsonify({'error': str(e)}), 500

@instagram_bp.route('/apify/scrape-urls', methods=['POST'])
def scrape_post_urls():
    """Scrape specific Instagram posts by URL via Apify"""
    from flask import current_app
    apify_manager = current_app.config.get('apify_manager')
    
    if not apify_manager:
        return jsonify({'error': 'Apify not configured'}), 400
    
    try:
        data = request.json
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({'error': 'URLs are required'}), 400
        
        logger.info(f"Scraping {len(urls)} URLs via Apify")
        
        # Scrape posts using Apify
        posts = apify_manager.scraper.scrape_post_urls(urls)
        
        return jsonify({
            'success': True,
            'urls_count': len(urls),
            'posts_count': len(posts),
            'posts': posts,
            'message': f'Successfully scraped {len(posts)} posts from {len(urls)} URLs'
        })
        
    except Exception as e:
        logger.error(f"Error scraping URLs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@instagram_bp.route('/apify/profile/<username>')
def get_user_profile(username):
    """Get Instagram user profile information via Apify"""
    from flask import current_app
    apify_manager = current_app.config.get('apify_manager')
    
    if not apify_manager:
        return jsonify({'error': 'Apify not configured'}), 400
    
    try:
        username = username.replace('@', '')
        logger.info(f"Getting profile for @{username} via Apify")
        
        profile = apify_manager.scraper.get_user_profile(username)
        
        if not profile:
            return jsonify({'error': f'Profile not found for @{username}'}), 404
        
        return jsonify({
            'success': True,
            'profile': profile
        })
        
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        return jsonify({'error': str(e)}), 500

@instagram_bp.route('/apify/import-to-wordpress', methods=['POST'])
def import_apify_to_wordpress():
    """Import Apify-scraped posts directly to WordPress"""
    try:
        data = request.json
        posts = data.get('posts', [])
        
        if not posts:
            return jsonify({'error': 'Posts data is required'}), 400
        
        # Get MCP client from Flask app context
        from flask import current_app
        mcp_client = current_app.config.get('mcp_client')
        
        imported_posts = []
        
        for post in posts:
            try:
                logger.info(f"Importing Apify post: {post.get('shortcode', 'unknown')}")
                
                # Upload image to WordPress media library
                media_id = None
                if post.get('image_url'):
                    media_result = mcp_client.upload_media(
                        url=post['image_url'],
                        title=f"Instagram import - @{post.get('username')} - {post.get('caption', '')[:50]}",
                        alt=post.get('caption', '')[:100]
                    )
                    
                    if media_result and 'id' in media_result:
                        media_id = media_result['id']
                
                # Create WordPress post title
                post_title = f"Instagram Post from @{post.get('username')} - {datetime.now().strftime('%Y-%m-%d')}"
                if post.get('caption'):
                    # Use first line of caption as title if available
                    first_line = post['caption'].split('\n')[0][:50]
                    if first_line and not first_line.startswith('#'):
                        post_title = first_line
                
                # Enhanced content with engagement metrics
                content = post.get('caption', '')
                if post.get('likes_count') or post.get('comments_count'):
                    content += f"\n\n---\n📊 **Engagement**: {post.get('likes_count', 0)} likes, {post.get('comments_count', 0)} comments"
                
                # Create WordPress post
                wp_result = mcp_client.create_post(
                    title=post_title,
                    content=content,
                    status='draft'  # Start as draft
                )
                
                # Parse post ID from response
                post_id = None
                if isinstance(wp_result, dict) and 'ID' in wp_result:
                    post_id = wp_result['ID']
                elif isinstance(wp_result, str) and 'Post created ID' in wp_result:
                    import re
                    match = re.search(r'Post created ID (\d+)', wp_result)
                    if match:
                        post_id = int(match.group(1))
                
                # Add enhanced Instagram metadata
                if post_id:
                    meta_fields = {
                        'instagram_post_url': post.get('post_url', ''),
                        'instagram_id': post.get('id', ''),
                        'instagram_shortcode': post.get('shortcode', ''),
                        'instagram_username': post.get('username', ''),
                        'instagram_hashtags': ','.join(post.get('hashtags', [])),
                        'instagram_media_type': post.get('media_type', 'IMAGE'),
                        'instagram_likes_count': str(post.get('likes_count', 0)),
                        'instagram_comments_count': str(post.get('comments_count', 0)),
                        'instagram_date_posted': post.get('date_posted', ''),
                        'import_method': 'apify_scraper',
                        'import_date': datetime.now().isoformat(),
                        'apify_raw_data': str(post.get('raw_data', {}))[:1000]  # Truncated raw data
                    }
                    
                    # Add metadata as custom fields
                    for key, value in meta_fields.items():
                        try:
                            mcp_client.call_mcp_function('wp_update_post_meta', {
                                'ID': post_id,
                                'key': key,
                                'value': value
                            })
                        except Exception as e:
                            logger.warning(f"Could not add meta field {key}: {e}")
                
                # Set featured image if we have one
                if media_id and post_id:
                    try:
                        mcp_client.set_featured_image(post_id, media_id)
                    except Exception as e:
                        logger.warning(f"Could not set featured image: {e}")
                
                imported_posts.append({
                    'instagram_post': post,
                    'wordpress_post': wp_result,
                    'media_id': media_id,
                    'post_id': post_id
                })
                
            except Exception as e:
                logger.error(f"Error importing post {post.get('shortcode', 'unknown')}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'imported_count': len(imported_posts),
            'total_posts': len(posts),
            'imported_posts': imported_posts,
            'message': f'Successfully imported {len(imported_posts)} of {len(posts)} posts to WordPress'
        })
        
    except Exception as e:
        logger.error(f"Error importing to WordPress: {str(e)}")
        return jsonify({'error': str(e)}), 500

@instagram_bp.route('/apify/bulk-import', methods=['POST'])
def bulk_import_user():
    """Scrape user posts via Apify and import directly to WordPress"""
    from flask import current_app
    apify_manager = current_app.config.get('apify_manager')
    
    if not apify_manager:
        return jsonify({'error': 'Apify not configured'}), 400
    
    try:
        data = request.json
        username = data.get('username', '').replace('@', '')
        limit = data.get('limit', 20)
        
        if not username:
            return jsonify({'error': 'Username is required'}), 400
        
        logger.info(f"Bulk import: scraping and importing @{username}, limit: {limit}")
        
        # Use the manager's built-in bulk import method
        result = apify_manager.import_user_posts_to_wordpress(username, limit, auto_publish=False)
        
        return jsonify(result)

        
    except Exception as e:
        logger.error(f"Error in bulk import: {str(e)}")
        return jsonify({'error': str(e)}), 500

@instagram_bp.route('/apify/cache/stats')
def get_cache_stats():
    """Get cache statistics"""
    from flask import current_app
    apify_manager = current_app.config.get('apify_manager')
    
    if not apify_manager:
        return jsonify({'error': 'Apify not configured'}), 400
    
    try:
        stats = apify_manager.scraper.get_cache_stats()
        return jsonify({
            'success': True,
            'cache_stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@instagram_bp.route('/apify/cache/clear-expired', methods=['POST'])
def clear_expired_cache():
    """Clear expired cache entries"""
    from flask import current_app
    apify_manager = current_app.config.get('apify_manager')
    
    if not apify_manager:
        return jsonify({'error': 'Apify not configured'}), 400
    
    try:
        removed_count = apify_manager.scraper.clear_expired_cache()
        return jsonify({
            'success': True,
            'removed_count': removed_count,
            'message': f'Cleared {removed_count} expired cache entries'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@instagram_bp.route('/apify/cache/clear-user/<username>', methods=['POST'])
def clear_user_cache(username):
    """Clear cache for specific user"""
    from flask import current_app
    apify_manager = current_app.config.get('apify_manager')
    
    if not apify_manager:
        return jsonify({'error': 'Apify not configured'}), 400
    
    try:
        username = username.replace('@', '')
        removed_count = apify_manager.scraper.clear_cache_for_user(username)
        return jsonify({
            'success': True,
            'removed_count': removed_count,
            'message': f'Cleared {removed_count} cache entries for @{username}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@instagram_bp.route('/apify/cache/clear-all', methods=['POST'])
def clear_all_cache():
    """Clear all cache entries"""
    from flask import current_app
    apify_manager = current_app.config.get('apify_manager')
    
    if not apify_manager:
        return jsonify({'error': 'Apify not configured'}), 400
    
    try:
        removed_count = apify_manager.scraper.cache.clear_all()
        return jsonify({
            'success': True,
            'removed_count': removed_count,
            'message': f'Cleared all cache: {removed_count} entries removed'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@instagram_bp.route('/apify/test-cache/<username>')
def test_cache_behavior(username):
    """Test endpoint to demonstrate cache behavior"""
    from flask import current_app
    apify_manager = current_app.config.get('apify_manager')
    
    if not apify_manager:
        return jsonify({'error': 'Apify not configured'}), 400
    
    try:
        import time
        username = username.replace('@', '')
        
        # First request - should hit API
        start_time = time.time()
        profile1 = apify_manager.scraper.get_user_profile(username, use_cache=True)
        first_duration = time.time() - start_time
        
        # Second request - should hit cache
        start_time = time.time()
        profile2 = apify_manager.scraper.get_user_profile(username, use_cache=True)
        second_duration = time.time() - start_time
        
        # Third request - bypass cache
        start_time = time.time()
        profile3 = apify_manager.scraper.get_user_profile(username, use_cache=False)
        third_duration = time.time() - start_time
        
        return jsonify({
            'success': True,
            'username': username,
            'test_results': {
                'first_request': {
                    'duration_seconds': round(first_duration, 3),
                    'source': 'API (cache miss)',
                    'profile_found': bool(profile1)
                },
                'second_request': {
                    'duration_seconds': round(second_duration, 3),
                    'source': 'Cache (should be much faster)',
                    'profile_found': bool(profile2)
                },
                'third_request': {
                    'duration_seconds': round(third_duration, 3),
                    'source': 'API (cache bypassed)',
                    'profile_found': bool(profile3)
                }
            },
            'cache_stats': apify_manager.scraper.get_cache_stats(),
            'message': f'Cache test completed for @{username}. Second request should be much faster than first/third.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@instagram_bp.route('/apify/debug/find-actors')
def find_instagram_actors():
    """Find available Instagram actors on Apify"""
    from flask import current_app
    apify_manager = current_app.config.get('apify_manager')
    
    if not apify_manager:
        return jsonify({'error': 'Apify not configured'}), 400
    
    try:
        # Test current actor ID
        current_available = apify_manager.scraper.scraper.test_actor_availability(
            apify_manager.scraper.scraper.actor_id
        )
        
        # Find Instagram actors
        actors = apify_manager.scraper.scraper.find_instagram_actors()
        
        # Test some common actor IDs
        common_ids = [
            'apify/instagram-scraper',
            'apify/instagram-post-scraper',
            'dtrungtin/instagram-scraper',
            'jaroslavhejlek/instagram-scraper'
        ]
        
        tested_actors = []
        for actor_id in common_ids:
            available = apify_manager.scraper.scraper.test_actor_availability(actor_id)
            tested_actors.append({
                'id': actor_id,
                'available': available
            })
        
        return jsonify({
            'success': True,
            'current_actor': {
                'id': apify_manager.scraper.scraper.actor_id,
                'available': current_available
            },
            'found_actors': actors,
            'tested_common_actors': tested_actors
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@instagram_bp.route('/apify/debug/test-actor/<path:actor_id>')
def test_actor(actor_id):
    """Test if a specific actor ID works"""
    from flask import current_app
    apify_manager = current_app.config.get('apify_manager')
    
    if not apify_manager:
        return jsonify({'error': 'Apify not configured'}), 400
    
    try:
        # Test actor availability
        available = apify_manager.scraper.scraper.test_actor_availability(actor_id)
        
        return jsonify({
            'success': True,
            'actor_id': actor_id,
            'available': available,
            'message': f'Actor {actor_id} is {"available" if available else "not available"}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500