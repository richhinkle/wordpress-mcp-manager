#!/usr/bin/env python3
"""
Standalone WordPress MCP Manager
A Flask application that provides web interface for WordPress management via AIWU MCP
"""

from flask import Flask, request, jsonify, render_template_string, redirect, session
from flask_cors import CORS
import requests
import json
import os
import logging
from datetime import datetime
import time
import sys
import os
# Add the parent directory to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.integrations.instagram.manual_import import InstagramManualImport
from src.integrations.instagram.apify_scraper import ApifyInstagramScraper, ApifyInstagramManager
# from src.integrations.instagram.oauth import InstagramOAuth, InstagramTokenManager  # Commented out - using manual import instead

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WordPressMCPClient:
    """Direct MCP client for WordPress AIWU plugin"""
    
    def __init__(self, wordpress_url, access_token):
        self.wordpress_url = wordpress_url
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Standalone-WordPress-MCP/1.0'
        })
        
    def call_mcp_function(self, method, params=None):
        """Call WordPress MCP function directly"""
        if params is None:
            params = {}
            
        # Create MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": int(time.time()),
            "method": "tools/call",
            "params": {
                "name": method,
                "arguments": params
            }
        }
        
        try:
            # Make request to WordPress MCP endpoint
            url = f"{self.wordpress_url}?token={self.access_token}"
            
            logger.info(f"Calling MCP function: {method}")
            response = self.session.post(url, json=mcp_request, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    mcp_result = result['result']
                    
                    # Handle the nested content structure from AIWU MCP
                    if isinstance(mcp_result, dict) and 'content' in mcp_result:
                        content = mcp_result['content']
                        if isinstance(content, list) and len(content) > 0:
                            # Extract text from first content item
                            first_content = content[0]
                            if isinstance(first_content, dict) and 'text' in first_content:
                                text_data = first_content['text']
                                # Try to parse as JSON
                                try:
                                    parsed_data = json.loads(text_data)
                                    logger.info(f"Parsed MCP response for {method}: {type(parsed_data)}")
                                    return parsed_data
                                except json.JSONDecodeError:
                                    # Try to extract JSON from text like "Ping successful: {...}"
                                    import re
                                    json_match = re.search(r'\{.*\}', text_data, re.DOTALL)
                                    if json_match:
                                        try:
                                            parsed_data = json.loads(json_match.group())
                                            logger.info(f"Extracted JSON from MCP response for {method}: {type(parsed_data)}")
                                            return parsed_data
                                        except json.JSONDecodeError:
                                            pass
                                    # If not JSON, return the text as-is
                                    return text_data
                    
                    # If not the expected nested structure, return as-is
                    return mcp_result
                elif 'error' in result:
                    raise Exception(f"MCP Error: {result['error']}")
                else:
                    return result
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            raise Exception("Request timed out")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection failed - check WordPress site and MCP plugin")
        except Exception as e:
            logger.error(f"MCP call failed: {str(e)}")
            raise
    
    def ping(self):
        """Test connection to WordPress"""
        return self.call_mcp_function('mcp_ping')
    
    def get_posts(self, limit=20, post_status=None, search=None):
        """Get WordPress posts"""
        params = {'limit': limit}
        if post_status:
            params['post_status'] = post_status
        if search:
            params['search'] = search
        return self.call_mcp_function('wp_get_posts', params)
    
    def get_post(self, post_id):
        """Get single WordPress post"""
        return self.call_mcp_function('wp_get_post', {'ID': post_id})
    
    def create_post(self, title, content, excerpt=None, status='draft', post_type='post'):
        """Create WordPress post"""
        params = {
            'post_title': title,
            'post_content': content,
            'post_status': status,
            'post_type': post_type
        }
        if excerpt:
            params['post_excerpt'] = excerpt
        return self.call_mcp_function('wp_create_post', params)
    
    def update_post(self, post_id, fields):
        """Update WordPress post"""
        return self.call_mcp_function('wp_update_post', {
            'ID': post_id,
            'fields': fields
        })
    
    def delete_post(self, post_id, force=True):
        """Delete WordPress post"""
        return self.call_mcp_function('wp_delete_post', {
            'ID': post_id,
            'force': force
        })
    
    def list_plugins(self):
        """List WordPress plugins"""
        return self.call_mcp_function('wp_list_plugins')
    
    def get_users(self, limit=10):
        """Get WordPress users"""
        return self.call_mcp_function('wp_get_users', {'limit': limit})
    
    def upload_media(self, url, title=None, alt=None):
        """Upload media from URL"""
        params = {'url': url}
        if title:
            params['title'] = title
        if alt:
            params['alt'] = alt
        return self.call_mcp_function('wp_upload_media', params)
    
    def generate_ai_image(self, prompt, title=None):
        """Generate AI image via AIWU"""
        params = {'message': prompt}
        if title:
            params['title'] = title
        return self.call_mcp_function('aiwu_image', params)
    
    # Content Management - Missing Functions
    def count_posts(self, post_type='post'):
        """Count posts by status"""
        params = {}
        if post_type:
            params['post_type'] = post_type
        return self.call_mcp_function('wp_count_posts', params)
    
    # User Management - Missing Functions
    def create_user(self, user_login, user_email, user_pass=None, display_name=None, role=None):
        """Create WordPress user"""
        params = {
            'user_login': user_login,
            'user_email': user_email
        }
        if user_pass:
            params['user_pass'] = user_pass
        if display_name:
            params['display_name'] = display_name
        if role:
            params['role'] = role
        return self.call_mcp_function('wp_create_user', params)
    
    def update_user(self, user_id, fields):
        """Update WordPress user"""
        return self.call_mcp_function('wp_update_user', {
            'ID': user_id,
            'fields': fields
        })
    
    # Post Meta & Custom Fields
    def get_post_meta(self, post_id, key=None):
        """Get post meta/custom fields"""
        params = {'ID': post_id}
        if key:
            params['key'] = key
        return self.call_mcp_function('wp_get_post_meta', params)
    
    def update_post_meta(self, post_id, key=None, value=None, meta=None):
        """Update post meta/custom fields"""
        params = {'ID': post_id}
        if key and value is not None:
            params['key'] = key
            params['value'] = value
        elif meta:
            params['meta'] = meta
        return self.call_mcp_function('wp_update_post_meta', params)
    
    def delete_post_meta(self, post_id, key, value=None):
        """Delete post meta/custom fields"""
        params = {
            'ID': post_id,
            'key': key
        }
        if value is not None:
            params['value'] = value
        return self.call_mcp_function('wp_delete_post_meta', params)
    
    # Media Management - Missing Functions
    def get_media(self, limit=20, search=None, after=None, before=None):
        """Get media items"""
        params = {'limit': limit}
        if search:
            params['search'] = search
        if after:
            params['after'] = after
        if before:
            params['before'] = before
        return self.call_mcp_function('wp_get_media', params)
    
    def update_media(self, media_id, title=None, alt=None, caption=None, description=None):
        """Update media/attachment"""
        params = {'ID': media_id}
        if title:
            params['title'] = title
        if alt:
            params['alt'] = alt
        if caption:
            params['caption'] = caption
        if description:
            params['description'] = description
        return self.call_mcp_function('wp_update_media', params)
    
    def delete_media(self, media_id, force=True):
        """Delete media/attachment"""
        return self.call_mcp_function('wp_delete_media', {
            'ID': media_id,
            'force': force
        })
    
    def set_featured_image(self, post_id, media_id=None):
        """Set or remove featured image"""
        params = {'post_id': post_id}
        if media_id:
            params['media_id'] = media_id
        return self.call_mcp_function('wp_set_featured_image', params)
    
    def count_media(self, after=None, before=None):
        """Count media attachments"""
        params = {}
        if after:
            params['after'] = after
        if before:
            params['before'] = before
        return self.call_mcp_function('wp_count_media', params)
    
    # Taxonomies (Categories & Tags)
    def get_taxonomies(self, post_type=None):
        """Get taxonomies for post type"""
        params = {}
        if post_type:
            params['post_type'] = post_type
        return self.call_mcp_function('wp_get_taxonomies', params)
    
    def get_terms(self, taxonomy, limit=50, parent=None, search=None):
        """Get terms from taxonomy"""
        params = {'taxonomy': taxonomy}
        if limit:
            params['limit'] = limit
        if parent is not None:
            params['parent'] = parent
        if search:
            params['search'] = search
        return self.call_mcp_function('wp_get_terms', params)
    
    def create_term(self, taxonomy, term_name, description=None, parent=None, slug=None):
        """Create taxonomy term"""
        params = {
            'taxonomy': taxonomy,
            'term_name': term_name
        }
        if description:
            params['description'] = description
        if parent is not None:
            params['parent'] = parent
        if slug:
            params['slug'] = slug
        return self.call_mcp_function('wp_create_term', params)
    
    def update_term(self, term_id, taxonomy, name=None, description=None, parent=None, slug=None):
        """Update taxonomy term"""
        params = {
            'term_id': term_id,
            'taxonomy': taxonomy
        }
        if name:
            params['name'] = name
        if description:
            params['description'] = description
        if parent is not None:
            params['parent'] = parent
        if slug:
            params['slug'] = slug
        return self.call_mcp_function('wp_update_term', params)
    
    def delete_term(self, term_id, taxonomy):
        """Delete taxonomy term"""
        return self.call_mcp_function('wp_delete_term', {
            'term_id': term_id,
            'taxonomy': taxonomy
        })
    
    def get_post_terms(self, post_id, taxonomy=None):
        """Get terms attached to post"""
        params = {'ID': post_id}
        if taxonomy:
            params['taxonomy'] = taxonomy
        return self.call_mcp_function('wp_get_post_terms', params)
    
    def add_post_terms(self, post_id, terms, taxonomy=None, append=True):
        """Add terms to post"""
        params = {
            'ID': post_id,
            'terms': terms,
            'append': append
        }
        if taxonomy:
            params['taxonomy'] = taxonomy
        return self.call_mcp_function('wp_add_post_terms', params)
    
    def count_terms(self, taxonomy):
        """Count terms in taxonomy"""
        return self.call_mcp_function('wp_count_terms', {'taxonomy': taxonomy})
    
    # Comments
    def get_comments(self, limit=20, post_id=None, status=None, search=None, offset=None, paged=None):
        """Get comments"""
        params = {'limit': limit}
        if post_id:
            params['post_id'] = post_id
        if status:
            params['status'] = status
        if search:
            params['search'] = search
        if offset:
            params['offset'] = offset
        if paged:
            params['paged'] = paged
        return self.call_mcp_function('wp_get_comments', params)
    
    def create_comment(self, post_id, comment_content, comment_author=None, comment_author_email=None, 
                      comment_author_url=None, comment_approved='1'):
        """Create comment"""
        params = {
            'post_id': post_id,
            'comment_content': comment_content
        }
        if comment_author:
            params['comment_author'] = comment_author
        if comment_author_email:
            params['comment_author_email'] = comment_author_email
        if comment_author_url:
            params['comment_author_url'] = comment_author_url
        if comment_approved:
            params['comment_approved'] = comment_approved
        return self.call_mcp_function('wp_create_comment', params)
    
    def update_comment(self, comment_id, fields):
        """Update comment"""
        return self.call_mcp_function('wp_update_comment', {
            'comment_ID': comment_id,
            'fields': fields
        })
    
    def delete_comment(self, comment_id, force=True):
        """Delete comment"""
        return self.call_mcp_function('wp_delete_comment', {
            'comment_ID': comment_id,
            'force': force
        })
    
    # Site Options
    def get_option(self, key):
        """Get WordPress option"""
        return self.call_mcp_function('wp_get_option', {'key': key})
    
    def update_option(self, key, value):
        """Update WordPress option"""
        return self.call_mcp_function('wp_update_option', {
            'key': key,
            'value': value
        })
    
    # Post Types
    def get_post_types(self):
        """Get public post types"""
        return self.call_mcp_function('wp_get_post_types')

# Flask Application Setup
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
CORS(app)

# Instagram OAuth Configuration - COMMENTED OUT (using manual import instead)
# INSTAGRAM_CLIENT_ID = os.getenv('INSTAGRAM_CLIENT_ID')
# INSTAGRAM_CLIENT_SECRET = os.getenv('INSTAGRAM_CLIENT_SECRET')
# INSTAGRAM_REDIRECT_URI = os.getenv('INSTAGRAM_REDIRECT_URI', 'http://localhost:5000/auth/instagram/callback')

# Initialize Instagram OAuth and Token Manager - COMMENTED OUT
# instagram_oauth = None
# instagram_tokens = InstagramTokenManager()

# if INSTAGRAM_CLIENT_ID and INSTAGRAM_CLIENT_SECRET:
#     instagram_oauth = InstagramOAuth(INSTAGRAM_CLIENT_ID, INSTAGRAM_CLIENT_SECRET, INSTAGRAM_REDIRECT_URI)
#     logger.info("✅ Instagram OAuth configured")
# else:
#     logger.warning("⚠️ Instagram OAuth not configured - set INSTAGRAM_CLIENT_ID and INSTAGRAM_CLIENT_SECRET")

# Configuration from environment variables
WORDPRESS_URL = os.environ.get('WORDPRESS_URL', 'https://your-wordpress-site.com/wp-json/mcp/v1/sse')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', 'your-access-token-here')
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

app.secret_key = SECRET_KEY

# Initialize MCP client
mcp_client = WordPressMCPClient(WORDPRESS_URL, ACCESS_TOKEN)

# Store MCP client in app config for blueprint access
app.config['mcp_client'] = mcp_client

# Initialize Apify Instagram integration
APIFY_API_TOKEN = os.environ.get('APIFY_API_TOKEN')
apify_manager = None

if APIFY_API_TOKEN:
    apify_manager = ApifyInstagramManager(APIFY_API_TOKEN, mcp_client)
    logger.info("✅ Apify Instagram integration configured")
else:
    logger.warning("⚠️ Apify not configured - set APIFY_API_TOKEN for professional Instagram scraping")

# Store apify_manager in app config for blueprint access
app.config['apify_manager'] = apify_manager

# Initialize chat handler
from src.core.chat_handler import WordPressChatHandler
chat_handler = WordPressChatHandler(mcp_client)

# Register Instagram API routes
from src.api.instagram_routes import instagram_bp
app.register_blueprint(instagram_bp)

# Routes
@app.route('/')
def index():
    """Serve main web interface"""
    from src.core.templates import WEB_INTERFACE_HTML
    return render_template_string(WEB_INTERFACE_HTML)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        result = mcp_client.ping()
        
        # Handle different response formats from MCP
        site_name = None
        timestamp = None
        
        if isinstance(result, dict):
            site_name = result.get('name')
            timestamp = result.get('time')
        elif isinstance(result, str):
            # Parse the string response like "Ping successful: {...}"
            import re
            import json
            
            # Try to extract JSON from the string
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group())
                    site_name = json_data.get('name')
                    timestamp = json_data.get('time')
                except json.JSONDecodeError:
                    pass
        
        return jsonify({
            'status': 'ok',
            'wordpress_connected': True,
            'site_name': site_name,
            'timestamp': timestamp,
            'raw_response': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'wordpress_connected': False,
            'error': str(e)
        }), 500

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Get WordPress posts"""
    try:
        limit = request.args.get('limit', 20, type=int)
        status = request.args.get('status')
        search = request.args.get('search')
        
        posts = mcp_client.get_posts(limit=limit, post_status=status, search=search)
        return jsonify(posts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>')
def get_post(post_id):
    """Get single WordPress post"""
    try:
        post = mcp_client.get_post(post_id)
        return jsonify(post)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts', methods=['POST'])
def create_post():
    """Create WordPress post"""
    try:
        data = request.json
        result = mcp_client.create_post(
            title=data.get('title'),
            content=data.get('content'),
            excerpt=data.get('excerpt'),
            status=data.get('status', 'draft'),
            post_type=data.get('post_type', 'post')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """Update WordPress post"""
    try:
        data = request.json
        result = mcp_client.update_post(post_id, data.get('fields', {}))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Delete WordPress post"""
    try:
        force = request.args.get('force', 'true').lower() == 'true'
        result = mcp_client.delete_post(post_id, force=force)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/plugins')
def list_plugins():
    """List WordPress plugins"""
    try:
        plugins = mcp_client.list_plugins()
        return jsonify(plugins)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users')
def get_users():
    """Get WordPress users"""
    try:
        limit = request.args.get('limit', 10, type=int)
        users = mcp_client.get_users(limit=limit)
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/media/upload', methods=['POST'])
def upload_media():
    """Upload media from URL"""
    try:
        data = request.json
        result = mcp_client.upload_media(
            url=data.get('url'),
            title=data.get('title'),
            alt=data.get('alt')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/image', methods=['POST'])
def generate_ai_image():
    """Generate AI image"""
    try:
        data = request.json
        result = mcp_client.generate_ai_image(
            prompt=data.get('prompt'),
            title=data.get('title')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Process the message through chat handler
        response = chat_handler.process_message(message)
        
        return jsonify(response)
    except Exception as e:
        return jsonify({
            'type': 'error',
            'message': f'Chat error: {str(e)}',
            'suggestions': ['Try rephrasing your message', 'Ask for help']
        }), 500

@app.route('/api/chat/history')
def chat_history():
    """Get chat conversation history"""
    try:
        # Return last 20 messages
        history = chat_handler.conversation_history[-20:]
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Content Management - Additional Endpoints
@app.route('/api/posts/count')
def count_posts():
    """Count posts by status"""
    try:
        post_type = request.args.get('post_type', 'post')
        result = mcp_client.count_posts(post_type=post_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/post-types')
def get_post_types():
    """Get public post types"""
    try:
        result = mcp_client.get_post_types()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User Management - Additional Endpoints
@app.route('/api/users', methods=['POST'])
def create_user():
    """Create WordPress user"""
    try:
        data = request.json
        result = mcp_client.create_user(
            user_login=data.get('user_login'),
            user_email=data.get('user_email'),
            user_pass=data.get('user_pass'),
            display_name=data.get('display_name'),
            role=data.get('role')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update WordPress user"""
    try:
        data = request.json
        result = mcp_client.update_user(user_id, data.get('fields', {}))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Post Meta & Custom Fields
@app.route('/api/posts/<int:post_id>/meta')
def get_post_meta(post_id):
    """Get post meta/custom fields"""
    try:
        key = request.args.get('key')
        result = mcp_client.get_post_meta(post_id, key=key)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>/meta', methods=['POST', 'PUT'])
def update_post_meta(post_id):
    """Update post meta/custom fields"""
    try:
        data = request.json
        result = mcp_client.update_post_meta(
            post_id=post_id,
            key=data.get('key'),
            value=data.get('value'),
            meta=data.get('meta')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>/meta/<key>', methods=['DELETE'])
def delete_post_meta(post_id, key):
    """Delete post meta/custom fields"""
    try:
        value = request.args.get('value')
        result = mcp_client.delete_post_meta(post_id, key, value=value)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>/featured-image', methods=['POST', 'PUT'])
def set_featured_image(post_id):
    """Set featured image for post"""
    try:
        data = request.json
        media_id = data.get('media_id')
        result = mcp_client.set_featured_image(post_id, media_id=media_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Media Management - Additional Endpoints
@app.route('/api/media')
def get_media():
    """Get media items"""
    try:
        limit = request.args.get('limit', 20, type=int)
        search = request.args.get('search')
        after = request.args.get('after')
        before = request.args.get('before')
        
        result = mcp_client.get_media(
            limit=limit,
            search=search,
            after=after,
            before=before
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/media/<int:media_id>', methods=['PUT'])
def update_media(media_id):
    """Update media/attachment"""
    try:
        data = request.json
        result = mcp_client.update_media(
            media_id=media_id,
            title=data.get('title'),
            alt=data.get('alt'),
            caption=data.get('caption'),
            description=data.get('description')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/media/<int:media_id>', methods=['DELETE'])
def delete_media(media_id):
    """Delete media/attachment"""
    try:
        force = request.args.get('force', 'true').lower() == 'true'
        result = mcp_client.delete_media(media_id, force=force)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/media/count')
def count_media():
    """Count media attachments"""
    try:
        after = request.args.get('after')
        before = request.args.get('before')
        result = mcp_client.count_media(after=after, before=before)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Taxonomies (Categories & Tags)
@app.route('/api/taxonomies')
def get_taxonomies():
    """Get taxonomies"""
    try:
        post_type = request.args.get('post_type')
        result = mcp_client.get_taxonomies(post_type=post_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/taxonomies/<taxonomy>/terms')
def get_terms(taxonomy):
    """Get terms from taxonomy"""
    try:
        limit = request.args.get('limit', 50, type=int)
        parent = request.args.get('parent', type=int)
        search = request.args.get('search')
        
        result = mcp_client.get_terms(
            taxonomy=taxonomy,
            limit=limit,
            parent=parent,
            search=search
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/taxonomies/<taxonomy>/terms', methods=['POST'])
def create_term(taxonomy):
    """Create taxonomy term"""
    try:
        data = request.json
        result = mcp_client.create_term(
            taxonomy=taxonomy,
            term_name=data.get('term_name'),
            description=data.get('description'),
            parent=data.get('parent'),
            slug=data.get('slug')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/taxonomies/<taxonomy>/terms/<int:term_id>', methods=['PUT'])
def update_term(taxonomy, term_id):
    """Update taxonomy term"""
    try:
        data = request.json
        result = mcp_client.update_term(
            term_id=term_id,
            taxonomy=taxonomy,
            name=data.get('name'),
            description=data.get('description'),
            parent=data.get('parent'),
            slug=data.get('slug')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/taxonomies/<taxonomy>/terms/<int:term_id>', methods=['DELETE'])
def delete_term(taxonomy, term_id):
    """Delete taxonomy term"""
    try:
        result = mcp_client.delete_term(term_id, taxonomy)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/taxonomies/<taxonomy>/count')
def count_terms(taxonomy):
    """Count terms in taxonomy"""
    try:
        result = mcp_client.count_terms(taxonomy)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>/terms')
def get_post_terms(post_id):
    """Get terms attached to post"""
    try:
        taxonomy = request.args.get('taxonomy')
        result = mcp_client.get_post_terms(post_id, taxonomy=taxonomy)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>/terms', methods=['POST'])
def add_post_terms(post_id):
    """Add terms to post"""
    try:
        data = request.json
        result = mcp_client.add_post_terms(
            post_id=post_id,
            terms=data.get('terms'),
            taxonomy=data.get('taxonomy'),
            append=data.get('append', True)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Comments
@app.route('/api/comments')
def get_comments():
    """Get comments"""
    try:
        limit = request.args.get('limit', 20, type=int)
        post_id = request.args.get('post_id', type=int)
        status = request.args.get('status')
        search = request.args.get('search')
        offset = request.args.get('offset', type=int)
        paged = request.args.get('paged', type=int)
        
        result = mcp_client.get_comments(
            limit=limit,
            post_id=post_id,
            status=status,
            search=search,
            offset=offset,
            paged=paged
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/comments', methods=['POST'])
def create_comment():
    """Create comment"""
    try:
        data = request.json
        result = mcp_client.create_comment(
            post_id=data.get('post_id'),
            comment_content=data.get('comment_content'),
            comment_author=data.get('comment_author'),
            comment_author_email=data.get('comment_author_email'),
            comment_author_url=data.get('comment_author_url'),
            comment_approved=data.get('comment_approved', '1')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    """Update comment"""
    try:
        data = request.json
        result = mcp_client.update_comment(comment_id, data.get('fields', {}))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """Delete comment"""
    try:
        force = request.args.get('force', 'true').lower() == 'true'
        result = mcp_client.delete_comment(comment_id, force=force)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Site Options
@app.route('/api/options/<key>')
def get_option(key):
    """Get WordPress option"""
    try:
        result = mcp_client.get_option(key)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/options/<key>', methods=['POST', 'PUT'])
def update_option(key):
    """Update WordPress option"""
    try:
        data = request.json
        result = mcp_client.update_option(key, data.get('value'))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/posts')
def debug_posts():
    """Debug endpoint to see raw post data"""
    try:
        result = mcp_client.get_posts(limit=5)
        return jsonify({
            'type': str(type(result)),
            'content': result,
            'length': len(result) if hasattr(result, '__len__') else 'No length'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Instagram OAuth Routes - COMMENTED OUT (using manual import instead)
# @app.route('/auth/instagram')
# def instagram_auth():
#     """Start Instagram OAuth flow"""
#     logger.info("=== Instagram OAuth Debug ===")
#     logger.info(f"Instagram OAuth configured: {instagram_oauth is not None}")
#     
#     if not instagram_oauth:
#         logger.error("Instagram OAuth not configured")
#         return jsonify({'error': 'Instagram OAuth not configured'}), 500
#     
#     # Log configuration
#     logger.info(f"Client ID: {INSTAGRAM_CLIENT_ID}")
#     logger.info(f"Redirect URI: {INSTAGRAM_REDIRECT_URI}")
#     
#     # Generate state for security
#     state = os.urandom(16).hex()
#     session['oauth_state'] = state
#     logger.info(f"Generated state: {state}")
#     
#     auth_url = instagram_oauth.get_authorization_url(state=state)
#     logger.info(f"Generated auth URL: {auth_url}")
#     
#     return redirect(auth_url)

# @app.route('/auth/instagram/callback')
# def instagram_callback():
#     """Handle Instagram OAuth callback"""
#     if not instagram_oauth:
#         return jsonify({'error': 'Instagram OAuth not configured'}), 500
#     
#     # Verify state parameter
#     state = request.args.get('state')
#     if state != session.get('oauth_state'):
#         return jsonify({'error': 'Invalid state parameter'}), 400
#     
#     # Get authorization code
#     code = request.args.get('code')
#     if not code:
#         error = request.args.get('error')
#         return jsonify({'error': f'Authorization failed: {error}'}), 400
#     
#     try:
#         # Exchange code for token
#         token_data = instagram_oauth.exchange_code_for_token(code)
#         
#         if 'access_token' in token_data:
#             # Get user profile
#             profile = instagram_oauth.get_user_profile(token_data['access_token'])
#             
#             if profile:
#                 user_id = profile.get('id')
#                 username = profile.get('username')
#                 
#                 # Store token
#                 token_data['username'] = username
#                 instagram_tokens.store_token(user_id, token_data)
#                 
#                 # Store in session
#                 session['instagram_user_id'] = user_id
#                 session['instagram_username'] = username
#                 
#                 logger.info(f"✅ Instagram OAuth successful for @{username}")
#                 
#                 # Redirect to main app with success message
#                 return redirect('/?instagram_auth=success')
#             else:
#                 return jsonify({'error': 'Failed to get user profile'}), 500
#         else:
#             return jsonify({'error': 'Failed to get access token'}), 500
#             
#     except Exception as e:
#         logger.error(f"Instagram OAuth error: {e}")
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/instagram/status')
# def instagram_status():
#     """Check Instagram authentication status"""
#     user_id = session.get('instagram_user_id')
#     username = session.get('instagram_username')
#     
#     if user_id and instagram_tokens.get_token(user_id):
#         return jsonify({
#             'authenticated': True,
#             'user_id': user_id,
#             'username': username
#         })
#     else:
#         return jsonify({
#             'authenticated': False,
#             'auth_url': '/auth/instagram' if instagram_oauth else None
#         })

# @app.route('/api/instagram/disconnect', methods=['POST'])
# def instagram_disconnect():
#     """Disconnect Instagram account"""
#     user_id = session.get('instagram_user_id')
#     
#     if user_id:
#         instagram_tokens.remove_token(user_id)
#         session.pop('instagram_user_id', None)
#         session.pop('instagram_username', None)
#         
#         return jsonify({'success': True, 'message': 'Instagram account disconnected'})
#     else:
#         return jsonify({'error': 'No Instagram account connected'}), 400

# @app.route('/api/instagram/posts')
# def get_instagram_posts():
#     """Get Instagram posts for authenticated user"""
#     user_id = session.get('instagram_user_id')
#     username = session.get('instagram_username')
#     
#     if not user_id:
#         return jsonify({'error': 'Instagram authentication required'}), 401
#     
#     access_token = instagram_tokens.get_token(user_id)
#     if not access_token:
#         return jsonify({'error': 'Instagram token expired, please re-authenticate'}), 401
#     
#     try:
#         # Get user's media
#         media_list = instagram_oauth.get_user_media(access_token, limit=25)
#         
#         # Format posts
#         formatted_posts = []
#         for media in media_list:
#             formatted_post = instagram_oauth.format_instagram_post(media, username)
#             if formatted_post:
#                 formatted_posts.append(formatted_post)
#         
#         return jsonify({
#             'success': True,
#             'posts': formatted_posts,
#             'count': len(formatted_posts)
#         })
#         
#     except Exception as e:
#         logger.error(f"Error fetching Instagram posts: {e}")
#         return jsonify({'error': str(e)}), 500

# Instagram Import Routes
@app.route('/api/instagram/import-urls', methods=['POST'])
def import_instagram_urls():
    """Import Instagram posts from URLs"""
    try:
        data = request.json
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({'error': 'URLs are required'}), 400
        
        importer = InstagramManualImport()
        posts = importer.import_from_urls(urls)
        
        return jsonify({
            'success': True,
            'imported_count': len(posts),
            'posts': posts
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/instagram/import-to-wordpress', methods=['POST'])
def import_instagram_to_wordpress():
    """Import Instagram posts directly to WordPress"""
    try:
        data = request.json
        posts = data.get('posts', [])
        
        if not posts:
            return jsonify({'error': 'Posts data is required'}), 400
        
        imported_posts = []
        
        for post in posts:
            try:
                logger.info(f"Processing Instagram post: {post}")
                
                # Upload image to WordPress media library
                if post.get('image_url'):
                    media_result = mcp_client.upload_media(
                        url=post['image_url'],
                        title=f"Instagram import - {post.get('caption', '')[:50]}",
                        alt=post.get('caption', '')[:100]
                    )
                    
                    if media_result and 'id' in media_result:
                        media_id = media_result['id']
                    else:
                        media_id = None
                else:
                    media_id = None
                
                # Create WordPress post
                wp_post_data = {
                    'post_title': f"Instagram Post - {datetime.now().strftime('%Y-%m-%d')}",
                    'post_content': post.get('caption', ''),
                    'post_status': 'draft',  # Start as draft
                    'post_type': 'post'
                }
                
                # Add custom fields for Instagram data
                meta_input = {
                    'instagram_post_url': post.get('post_url', ''),
                    'instagram_shortcode': post.get('shortcode', ''),
                    'instagram_hashtags': ','.join(post.get('hashtags', [])),
                    'import_method': post.get('extraction_method', 'manual'),
                    'import_date': datetime.now().isoformat()
                }
                
                wp_result = mcp_client.create_post(
                    title=wp_post_data['post_title'],
                    content=wp_post_data['post_content'],
                    status=wp_post_data['post_status']
                )
                
                logger.info(f"WordPress create_post result: {wp_result}")
                logger.info(f"Result type: {type(wp_result)}")
                
                # Parse post ID from response (handle both dict and string formats)
                post_id = None
                if isinstance(wp_result, dict) and 'ID' in wp_result:
                    post_id = wp_result['ID']
                elif isinstance(wp_result, str) and 'Post created ID' in wp_result:
                    # Extract ID from string like "Post created ID 32"
                    import re
                    match = re.search(r'Post created ID (\d+)', wp_result)
                    if match:
                        post_id = int(match.group(1))
                
                if post_id:
                    # Add Instagram metadata as custom fields
                    for key, value in meta_input.items():
                        try:
                            mcp_client.call_mcp_function('wp_update_post_meta', {
                                'ID': post_id,
                                'key': key,
                                'value': value
                            })
                        except Exception as e:
                            logger.warning(f"Could not add meta field {key}: {e}")
                
                # Set featured image if we have one
                if media_id and wp_result and 'ID' in wp_result:
                    mcp_client.set_featured_image(wp_result['ID'], media_id)
                
                imported_posts.append({
                    'instagram_post': post,
                    'wordpress_post': wp_result,
                    'media_id': media_id
                })
                
            except Exception as e:
                logger.error(f"Error importing post {post.get('shortcode', 'unknown')}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'imported_count': len(imported_posts),
            'imported_posts': imported_posts
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Apify Instagram Integration Routes
@app.route('/api/instagram/apify/scrape-user', methods=['POST'])
def apify_scrape_user():
    """Scrape Instagram user posts via Apify"""
    if not apify_manager:
        return jsonify({'error': 'Apify integration not configured'}), 500
    
    try:
        data = request.json
        username = data.get('username', '').replace('@', '')
        limit = data.get('limit', 20)
        
        if not username:
            return jsonify({'error': 'Username is required'}), 400
        
        posts = apify_manager.scraper.scrape_user_posts(username, limit)
        
        return jsonify({
            'success': True,
            'username': username,
            'posts_count': len(posts),
            'posts': posts
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/instagram/apify/scrape-urls', methods=['POST'])
def apify_scrape_urls():
    """Scrape specific Instagram posts via Apify"""
    if not apify_manager:
        return jsonify({'error': 'Apify integration not configured'}), 500
    
    try:
        data = request.json
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({'error': 'URLs are required'}), 400
        
        posts = apify_manager.scraper.scrape_post_urls(urls)
        
        return jsonify({
            'success': True,
            'urls_count': len(urls),
            'posts_count': len(posts),
            'posts': posts
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/instagram/apify/import-user', methods=['POST'])
def apify_import_user_to_wordpress():
    """Import Instagram user posts directly to WordPress via Apify"""
    if not apify_manager:
        return jsonify({'error': 'Apify integration not configured'}), 500
    
    try:
        data = request.json
        username = data.get('username', '').replace('@', '')
        limit = data.get('limit', 10)
        auto_publish = data.get('auto_publish', False)
        
        if not username:
            return jsonify({'error': 'Username is required'}), 400
        
        result = apify_manager.import_user_posts_to_wordpress(
            username, limit, auto_publish
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/instagram/apify/profile', methods=['GET'])
def apify_get_profile():
    """Get Instagram user profile via Apify"""
    if not apify_manager:
        return jsonify({'error': 'Apify integration not configured'}), 500
    
    try:
        username = request.args.get('username', '').replace('@', '')
        
        if not username:
            return jsonify({'error': 'Username is required'}), 400
        
        profile = apify_manager.scraper.get_user_profile(username)
        
        return jsonify({
            'success': True,
            'profile': profile
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/instagram/apify/cost-estimate', methods=['POST'])
def apify_cost_estimate():
    """Estimate cost for Apify operation"""
    if not apify_manager:
        return jsonify({'error': 'Apify integration not configured'}), 500
    
    try:
        data = request.json
        operation_type = data.get('operation_type', 'user_posts')
        count = data.get('count', 10)
        
        estimate = apify_manager.scraper.estimate_cost(operation_type, count)
        
        return jsonify({
            'success': True,
            'estimate': estimate
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/instagram/apify/status')
def apify_status():
    """Check Apify integration status"""
    return jsonify({
        'configured': apify_manager is not None,
        'api_token_set': bool(APIFY_API_TOKEN),
        'features': [
            'Professional Instagram scraping',
            'Bulk user post import',
            'URL-based post scraping',
            'Profile information extraction',
            'Cost estimation',
            'Direct WordPress integration'
        ] if apify_manager else []
    })

# @app.route('/api/instagram/import-authenticated', methods=['POST'])
# def import_authenticated_instagram():
#     """Import posts from authenticated Instagram account - COMMENTED OUT (using manual import instead)"""
#     user_id = session.get('instagram_user_id')
#     username = session.get('instagram_username')
#     
#     if not user_id:
#         return jsonify({'error': 'Instagram authentication required'}), 401
#     
#     access_token = instagram_tokens.get_token(user_id)
#     if not access_token:
#         return jsonify({'error': 'Instagram token expired, please re-authenticate'}), 401
#     
#     try:
#         data = request.json
#         limit = data.get('limit', 10)  # Default to 10 posts
#         
#         # Get user's media
#         media_list = instagram_oauth.get_user_media(access_token, limit=limit)
#         
#         # Format posts
#         formatted_posts = []
#         for media in media_list:
#             formatted_post = instagram_oauth.format_instagram_post(media, username)
#             if formatted_post:
#                 formatted_posts.append(formatted_post)
#         
#         # Import to WordPress
#         imported_posts = []
#         
#         for post in formatted_posts:
#             try:
#                 # Upload image to WordPress media library
#                 if post.get('image_url'):
#                     media_result = mcp_client.upload_media_from_url(
#                         url=post['image_url'],
#                         title=f"Instagram import - @{username} - {post.get('caption', '')[:50]}",
#                         alt=post.get('caption', '')[:100]
#                     )
#                     
#                     if media_result and 'id' in media_result:
#                         media_id = media_result['id']
#                     else:
#                         media_id = None
#                 else:
#                     media_id = None
#                 
#                 # Create WordPress post
#                 post_title = f"Instagram Post from @{username} - {datetime.now().strftime('%Y-%m-%d')}"
#                 if post.get('caption'):
#                     # Use first line of caption as title if available
#                     first_line = post['caption'].split('\n')[0][:50]
#                     if first_line:
#                         post_title = first_line
#                 
#                 # Add custom fields for Instagram data
#                 meta_input = {
#                     'instagram_post_url': post.get('post_url', ''),
#                     'instagram_id': post.get('id', ''),
#                     'instagram_username': username,
#                     'instagram_hashtags': ','.join(post.get('hashtags', [])),
#                     'instagram_media_type': post.get('media_type', 'IMAGE'),
#                     'import_method': 'instagram_oauth_api',
#                     'import_date': datetime.now().isoformat()
#                 }
#                 
#                 wp_result = mcp_client.create_post(
#                     title=post_title,
#                     content=post.get('caption', ''),
#                     status='draft'  # Start as draft
#                 )
#                 
#                 # Parse post ID from response (handle both dict and string formats)
#                 post_id = None
#                 if isinstance(wp_result, dict) and 'ID' in wp_result:
#                     post_id = wp_result['ID']
#                 elif isinstance(wp_result, str) and 'Post created ID' in wp_result:
#                     # Extract ID from string like "Post created ID 32"
#                     import re
#                     match = re.search(r'Post created ID (\d+)', wp_result)
#                     if match:
#                         post_id = int(match.group(1))
#                 
#                 if post_id:
#                     # Add Instagram metadata as custom fields
#                     for key, value in meta_input.items():
#                         try:
#                             mcp_client.call_mcp_function('wp_update_post_meta', {
#                                 'ID': post_id,
#                                 'key': key,
#                                 'value': value
#                             })
#                         except Exception as e:
#                             logger.warning(f"Could not add meta field {key}: {e}")
#                 
#                 # Set featured image if we have one
#                 if media_id and wp_result and 'ID' in wp_result:
#                     mcp_client.set_featured_image(wp_result['ID'], media_id)
#                 
#                 imported_posts.append({
#                     'instagram_post': post,
#                     'wordpress_post': wp_result,
#                     'media_id': media_id
#                 })
#                 
#             except Exception as e:
#                 logger.error(f"Error importing post {post.get('id', 'unknown')}: {e}")
#                 continue
#         
#         return jsonify({
#             'success': True,
#             'imported_count': len(imported_posts),
#             'imported_posts': imported_posts,
#             'total_available': len(formatted_posts)
#         })
#         
#     except Exception as e:
#         logger.error(f"Error importing authenticated Instagram posts: {e}")
#         return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Configuration check
    if not WORDPRESS_URL or not ACCESS_TOKEN:
        logger.error("Missing required environment variables: WORDPRESS_URL, ACCESS_TOKEN")
        exit(1)
    
    # Test connection on startup
    try:
        result = mcp_client.ping()
        logger.info(f"Successfully connected to WordPress: {result.get('name')}")
    except Exception as e:
        logger.warning(f"Could not connect to WordPress on startup: {e}")
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting WordPress Manager on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)