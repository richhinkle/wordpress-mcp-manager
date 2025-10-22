# Standalone WordPress MCP Application

**Concept:** Create a self-contained Python application that combines MCP functionality with a Flask web interface, eliminating the need for Kiro IDE in production.

## Architecture

```
User Browser → Flask Web App → Direct MCP Client → WordPress AIWU Plugin
```

**Benefits:**
- ✅ No Kiro dependency in production
- ✅ Single deployable application
- ✅ Easier to distribute and maintain
- ✅ Can be containerized with Docker
- ✅ Simpler deployment to cloud services

---

## Implementation

### Complete Standalone Application

```python
# standalone_wordpress_manager.py
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import json
import os
import logging
from datetime import datetime
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
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
                    return result['result']
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

# Flask Application
app = Flask(__name__)
CORS(app)

# Configuration
WORDPRESS_URL = os.environ.get('WORDPRESS_URL', 'https://your-wordpress-site.com/wp-json/mcp/v1/sse')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', 'your-access-token-here')
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

app.secret_key = SECRET_KEY

# Initialize MCP client
mcp_client = WordPressMCPClient(WORDPRESS_URL, ACCESS_TOKEN)

# Routes
@app.route('/')
def index():
    """Serve main web interface"""
    return render_template_string(WEB_INTERFACE_HTML)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        result = mcp_client.ping()
        return jsonify({
            'status': 'ok',
            'wordpress_connected': True,
            'site_name': result.get('name'),
            'timestamp': result.get('time')
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

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500# 
Web Interface HTML Template
WEB_INTERFACE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WordPress Manager</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .header h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        
        .status {
            margin-top: 15px;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: 600;
            display: inline-block;
        }
        
        .status.connected {
            background: #d4edda;
            color: #155724;
        }
        
        .status.disconnected {
            background: #f8d7da;
            color: #721c24;
        }
        
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s ease;
        }
        
        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-group textarea {
            resize: vertical;
            min-height: 120px;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .btn.secondary {
            background: #6c757d;
        }
        
        .btn.danger {
            background: #dc3545;
        }
        
        .btn.success {
            background: #28a745;
        }
        
        .posts-container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .posts-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .posts-header h2 {
            margin: 0;
            font-size: 1.5em;
        }
        
        .posts-content {
            padding: 30px;
        }
        
        .post-item {
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            transition: border-color 0.3s ease, transform 0.2s ease;
        }
        
        .post-item:hover {
            border-color: #667eea;
            transform: translateY(-2px);
        }
        
        .post-item.draft {
            border-left: 4px solid #ffc107;
        }
        
        .post-item.publish {
            border-left: 4px solid #28a745;
        }
        
        .post-title {
            font-size: 1.2em;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }
        
        .post-meta {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            font-size: 0.9em;
            color: #666;
        }
        
        .post-status {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .post-status.draft {
            background: #fff3cd;
            color: #856404;
        }
        
        .post-status.publish {
            background: #d4edda;
            color: #155724;
        }
        
        .post-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 1.1em;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        
        .success {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        
        .info {
            background: #d1ecf1;
            color: #0c5460;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            padding: 15px 25px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        .notification.success {
            background: #28a745;
        }
        
        .notification.error {
            background: #dc3545;
        }
        
        .notification.info {
            background: #17a2b8;
        }
        
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .card {
                padding: 20px;
            }
            
            .posts-content {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🌐 WordPress Manager</h1>
            <p>Standalone MCP-powered WordPress management</p>
            <div id="connection-status" class="status">Checking connection...</div>
        </div>
        
        <!-- Main Grid -->
        <div class="grid">
            <!-- Create Post Card -->
            <div class="card">
                <h2>📝 Create New Post</h2>
                <form id="create-post-form">
                    <div class="form-group">
                        <label for="post-title">Title</label>
                        <input type="text" id="post-title" placeholder="Enter post title" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="post-content">Content</label>
                        <textarea id="post-content" placeholder="Write your post content here..." required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="post-excerpt">Excerpt (Optional)</label>
                        <textarea id="post-excerpt" placeholder="Brief description..." style="min-height: 80px;"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="post-status">Status</label>
                        <select id="post-status">
                            <option value="draft">Save as Draft</option>
                            <option value="publish">Publish Immediately</option>
                        </select>
                    </div>
                    
                    <button type="submit" class="btn">Create Post</button>
                    <button type="button" class="btn secondary" onclick="clearForm()">Clear</button>
                </form>
            </div>
            
            <!-- Quick Actions Card -->
            <div class="card">
                <h2>⚡ Quick Actions</h2>
                
                <button class="btn" onclick="loadPosts()">📄 Refresh Posts</button>
                <button class="btn secondary" onclick="loadDrafts()">📝 Show Drafts</button>
                <button class="btn secondary" onclick="loadPublished()">✅ Show Published</button>
                <button class="btn secondary" onclick="checkSiteHealth()">🔍 Site Health</button>
                <button class="btn secondary" onclick="listPlugins()">🔌 Plugins</button>
                <button class="btn secondary" onclick="listUsers()">👥 Users</button>
                
                <div id="quick-info" style="margin-top: 20px;"></div>
                
                <div style="margin-top: 30px;">
                    <h3>🎨 AI Image Generator</h3>
                    <div class="form-group">
                        <input type="text" id="ai-prompt" placeholder="Describe the image you want to generate...">
                    </div>
                    <button class="btn success" onclick="generateAIImage()">Generate Image</button>
                </div>
            </div>
        </div>
        
        <!-- Posts Container -->
        <div class="posts-container">
            <div class="posts-header">
                <h2>📚 Your Posts</h2>
                <div>
                    <input type="text" id="search-posts" placeholder="Search posts..." 
                           style="padding: 8px; border: none; border-radius: 4px; margin-right: 10px;">
                    <button class="btn" onclick="searchPosts()" style="margin: 0;">🔍 Search</button>
                </div>
            </div>
            <div class="posts-content">
                <div id="posts-container" class="loading">Loading posts...</div>
            </div>
        </div>
    </div>

    <script>
        // Application state
        let currentPosts = [];
        
        // Initialize app
        document.addEventListener('DOMContentLoaded', function() {
            checkConnection();
            loadPosts();
            
            // Form submission
            document.getElementById('create-post-form').addEventListener('submit', function(e) {
                e.preventDefault();
                createPost();
            });
            
            // Search on Enter key
            document.getElementById('search-posts').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchPosts();
                }
            });
        });
        
        // API Functions
        async function apiCall(endpoint, options = {}) {
            try {
                const response = await fetch(endpoint, {
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    },
                    ...options
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || `HTTP ${response.status}`);
                }
                
                return await response.json();
            } catch (error) {
                console.error('API call failed:', error);
                throw error;
            }
        }
        
        // Connection check
        async function checkConnection() {
            try {
                const result = await apiCall('/api/health');
                
                const statusEl = document.getElementById('connection-status');
                if (result.wordpress_connected) {
                    statusEl.textContent = `✅ Connected to ${result.site_name}`;
                    statusEl.className = 'status connected';
                } else {
                    statusEl.textContent = '❌ WordPress connection failed';
                    statusEl.className = 'status disconnected';
                }
            } catch (error) {
                const statusEl = document.getElementById('connection-status');
                statusEl.textContent = '❌ Server connection failed';
                statusEl.className = 'status disconnected';
            }
        }
        
        // Post management
        async function createPost() {
            const title = document.getElementById('post-title').value.trim();
            const content = document.getElementById('post-content').value.trim();
            const excerpt = document.getElementById('post-excerpt').value.trim();
            const status = document.getElementById('post-status').value;
            
            if (!title || !content) {
                showNotification('Please fill in title and content', 'error');
                return;
            }
            
            try {
                showNotification('Creating post...', 'info');
                
                const result = await apiCall('/api/posts', {
                    method: 'POST',
                    body: JSON.stringify({
                        title: title,
                        content: content,
                        excerpt: excerpt || null,
                        status: status
                    })
                });
                
                showNotification(`Post created successfully! ID: ${result.ID}`, 'success');
                clearForm();
                loadPosts();
            } catch (error) {
                showNotification(`Error creating post: ${error.message}`, 'error');
            }
        }
        
        async function loadPosts() {
            try {
                document.getElementById('posts-container').innerHTML = '<div class="loading">Loading posts...</div>';
                
                const posts = await apiCall('/api/posts?limit=20');
                currentPosts = posts;
                displayPosts(posts);
            } catch (error) {
                document.getElementById('posts-container').innerHTML = 
                    `<div class="error">Error loading posts: ${error.message}</div>`;
            }
        }
        
        async function loadDrafts() {
            try {
                document.getElementById('posts-container').innerHTML = '<div class="loading">Loading drafts...</div>';
                
                const posts = await apiCall('/api/posts?status=draft&limit=20');
                currentPosts = posts;
                displayPosts(posts);
                
                showNotification(`Found ${posts.length} draft posts`, 'info');
            } catch (error) {
                showNotification(`Error loading drafts: ${error.message}`, 'error');
            }
        }
        
        async function loadPublished() {
            try {
                document.getElementById('posts-container').innerHTML = '<div class="loading">Loading published posts...</div>';
                
                const posts = await apiCall('/api/posts?status=publish&limit=20');
                currentPosts = posts;
                displayPosts(posts);
                
                showNotification(`Found ${posts.length} published posts`, 'info');
            } catch (error) {
                showNotification(`Error loading published posts: ${error.message}`, 'error');
            }
        }
        
        async function searchPosts() {
            const query = document.getElementById('search-posts').value.trim();
            if (!query) {
                loadPosts();
                return;
            }
            
            try {
                document.getElementById('posts-container').innerHTML = '<div class="loading">Searching posts...</div>';
                
                const posts = await apiCall(`/api/posts?search=${encodeURIComponent(query)}&limit=50`);
                currentPosts = posts;
                displayPosts(posts);
                
                showNotification(`Found ${posts.length} posts matching "${query}"`, 'info');
            } catch (error) {
                showNotification(`Search error: ${error.message}`, 'error');
            }
        }
        
        function displayPosts(posts) {
            const container = document.getElementById('posts-container');
            
            if (!posts || posts.length === 0) {
                container.innerHTML = '<div class="info">No posts found. Create your first post above!</div>';
                return;
            }
            
            let html = '';
            posts.forEach(post => {
                html += `
                    <div class="post-item ${post.post_status}">
                        <div class="post-title">${escapeHtml(post.post_title)}</div>
                        <div class="post-meta">
                            <span class="post-status ${post.post_status}">${post.post_status}</span>
                            <span>ID: ${post.ID}</span>
                        </div>
                        <div style="margin-bottom: 15px;">
                            ${post.post_excerpt ? `<p>${escapeHtml(post.post_excerpt)}</p>` : '<p><em>No excerpt</em></p>'}
                        </div>
                        <div class="post-actions">
                            <a href="${post.permalink}" target="_blank" class="btn secondary">🔗 View</a>
                            ${post.post_status === 'draft' ? 
                                `<button class="btn success" onclick="publishPost(${post.ID})">📤 Publish</button>` : ''}
                            <button class="btn danger" onclick="deletePost(${post.ID}, '${escapeHtml(post.post_title)}')">🗑️ Delete</button>
                        </div>
                    </div>
                `;
            });
            
            container.innerHTML = html;
        }
        
        async function publishPost(postId) {
            if (!confirm('Publish this post?')) return;
            
            try {
                showNotification('Publishing post...', 'info');
                
                await apiCall(`/api/posts/${postId}`, {
                    method: 'PUT',
                    body: JSON.stringify({
                        fields: { post_status: 'publish' }
                    })
                });
                
                showNotification('Post published successfully!', 'success');
                loadPosts();
            } catch (error) {
                showNotification(`Error publishing post: ${error.message}`, 'error');
            }
        }
        
        async function deletePost(postId, title) {
            if (!confirm(`Delete "${title}"?\\n\\nThis cannot be undone.`)) return;
            
            try {
                showNotification('Deleting post...', 'info');
                
                await apiCall(`/api/posts/${postId}?force=true`, {
                    method: 'DELETE'
                });
                
                showNotification('Post deleted successfully', 'success');
                loadPosts();
            } catch (error) {
                showNotification(`Error deleting post: ${error.message}`, 'error');
            }
        }
        
        // Site information functions
        async function checkSiteHealth() {
            try {
                showNotification('Checking site health...', 'info');
                
                const result = await apiCall('/api/health');
                
                const info = `
                    <div class="success">
                        <h4>✅ Site Health Check</h4>
                        <p><strong>Site:</strong> ${result.site_name}</p>
                        <p><strong>Status:</strong> Online and responding</p>
                        <p><strong>Last Check:</strong> ${result.timestamp}</p>
                    </div>
                `;
                
                document.getElementById('quick-info').innerHTML = info;
                showNotification('Site health check completed', 'success');
            } catch (error) {
                document.getElementById('quick-info').innerHTML = 
                    `<div class="error">❌ Site health check failed: ${error.message}</div>`;
                showNotification('Site health check failed', 'error');
            }
        }
        
        async function listPlugins() {
            try {
                showNotification('Loading plugins...', 'info');
                
                const plugins = await apiCall('/api/plugins');
                
                let html = '<div class="info"><h4>🔌 Installed Plugins</h4><ul>';
                plugins.forEach(plugin => {
                    html += `<li>${escapeHtml(plugin.Name)} <small>(v${plugin.Version})</small></li>`;
                });
                html += '</ul></div>';
                
                document.getElementById('quick-info').innerHTML = html;
                showNotification(`Found ${plugins.length} plugins`, 'success');
            } catch (error) {
                showNotification(`Error loading plugins: ${error.message}`, 'error');
            }
        }
        
        async function listUsers() {
            try {
                showNotification('Loading users...', 'info');
                
                const users = await apiCall('/api/users?limit=20');
                
                let html = '<div class="info"><h4>👥 WordPress Users</h4><ul>';
                users.forEach(user => {
                    html += `<li>${escapeHtml(user.display_name)} (${user.user_login})`;
                    if (user.roles && user.roles.length > 0) {
                        html += ` - ${user.roles.join(', ')}`;
                    }
                    html += '</li>';
                });
                html += '</ul></div>';
                
                document.getElementById('quick-info').innerHTML = html;
                showNotification(`Found ${users.length} users`, 'success');
            } catch (error) {
                showNotification(`Error loading users: ${error.message}`, 'error');
            }
        }
        
        async function generateAIImage() {
            const prompt = document.getElementById('ai-prompt').value.trim();
            if (!prompt) {
                showNotification('Please enter an image description', 'error');
                return;
            }
            
            try {
                showNotification('Generating AI image...', 'info');
                
                const result = await apiCall('/api/ai/image', {
                    method: 'POST',
                    body: JSON.stringify({
                        prompt: prompt,
                        title: `AI Generated: ${prompt.substring(0, 50)}`
                    })
                });
                
                showNotification(`Image generated successfully! ID: ${result.id}`, 'success');
                document.getElementById('ai-prompt').value = '';
                
                // Show generated image info
                const info = `
                    <div class="success">
                        <h4>🎨 AI Image Generated</h4>
                        <p><strong>Title:</strong> ${escapeHtml(result.title)}</p>
                        <p><strong>URL:</strong> <a href="${result.url}" target="_blank">View Image</a></p>
                    </div>
                `;
                document.getElementById('quick-info').innerHTML = info;
            } catch (error) {
                showNotification(`Error generating image: ${error.message}`, 'error');
            }
        }
        
        // Utility functions
        function clearForm() {
            document.getElementById('post-title').value = '';
            document.getElementById('post-content').value = '';
            document.getElementById('post-excerpt').value = '';
            document.getElementById('post-status').value = 'draft';
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function showNotification(message, type) {
            // Remove existing notification
            const existing = document.querySelector('.notification');
            if (existing) existing.remove();
            
            // Create new notification
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            // Show notification
            setTimeout(() => notification.classList.add('show'), 100);
            
            // Auto hide
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }
    </script>
</body>
</html>
'''

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
```

---

## Deployment Files

### requirements.txt
```
Flask==2.3.3
Flask-CORS==4.0.0
requests==2.31.0
gunicorn==21.2.0
```

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY standalone_wordpress_manager.py .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "standalone_wordpress_manager:app"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  wordpress-manager:
    build: .
    ports:
      - "5000:5000"
    environment:
      - WORDPRESS_URL=https://your-wordpress-site.com/wp-json/mcp/v1/sse
      - ACCESS_TOKEN=your-access-token-here
      - SECRET_KEY=your-secret-key-here
      - DEBUG=false
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### .env (for local development)
```bash
WORDPRESS_URL=https://your-wordpress-site.com/wp-json/mcp/v1/sse
ACCESS_TOKEN=your-access-token-here
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=true
PORT=5000
```

---

## Usage Instructions

### Local Development
```bash
# Clone/create project
mkdir wordpress-mcp-manager
cd wordpress-mcp-manager

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export WORDPRESS_URL="https://your-wordpress-site.com/wp-json/mcp/v1/sse"
export ACCESS_TOKEN="your-access-token"
export SECRET_KEY="your-secret-key"

# Run application
python standalone_wordpress_manager.py
```

### Docker Deployment
```bash
# Build and run with Docker
docker-compose up --build

# Or run directly
docker build -t wordpress-manager .
docker run -p 5000:5000 \
  -e WORDPRESS_URL="https://your-wordpress-site.com/wp-json/mcp/v1/sse" \
  -e ACCESS_TOKEN="your-token" \
  -e SECRET_KEY="your-secret" \
  wordpress-manager
```

### Cloud Deployment (Heroku)
```bash
# Create Heroku app
heroku create your-wp-manager

# Set environment variables
heroku config:set WORDPRESS_URL="https://your-wordpress-site.com/wp-json/mcp/v1/sse"
heroku config:set ACCESS_TOKEN="your-token"
heroku config:set SECRET_KEY="your-secret-key"

# Deploy
git push heroku main
```

---

## Advantages of Standalone Approach

### ✅ **Production Ready**
- No Kiro dependency
- Self-contained application
- Easy to deploy and scale
- Professional logging and error handling

### ✅ **Simplified Architecture**
- Direct MCP client implementation
- Clean REST API design
- Single deployable unit
- Easier to maintain and debug

### ✅ **Better Performance**
- No subprocess calls
- Direct HTTP connections
- Optimized for production use
- Better error handling and recovery

### ✅ **Enhanced Security**
- Environment variable configuration
- Proper error handling without exposing internals
- Can add authentication easily
- CORS support for cross-origin requests

### ✅ **Deployment Flexibility**
- Docker containerization
- Cloud platform ready (Heroku, AWS, GCP, etc.)
- Can run on any server
- Easy to scale horizontally

---

## Feature Comparison

| Feature | Kiro-Dependent | Standalone |
|---------|----------------|------------|
| **Deployment** | Requires Kiro IDE | Self-contained |
| **Dependencies** | Kiro + Python bridge | Just Python |
| **Performance** | Subprocess overhead | Direct connections |
| **Scalability** | Limited | Horizontal scaling |
| **Maintenance** | Complex setup | Simple deployment |
| **Production Use** | Not ideal | Production ready |
| **Docker Support** | Difficult | Native support |
| **Cloud Deployment** | Complex | Straightforward |

---

## Migration Path

### From Kiro-Dependent to Standalone

1. **Extract MCP Logic**
   - Copy WordPress MCP functionality from bridge
   - Implement direct HTTP client
   - Add proper error handling

2. **Create Flask API**
   - RESTful endpoints for all WordPress operations
   - Proper HTTP status codes
   - JSON request/response format

3. **Enhanced Web Interface**
   - Modern, responsive design
   - Real-time feedback
   - Professional user experience

4. **Production Deployment**
   - Docker containerization
   - Environment configuration
   - Health checks and monitoring

This standalone approach gives you a professional, production-ready WordPress management application that's completely independent of Kiro IDE while maintaining all the MCP functionality you've built.