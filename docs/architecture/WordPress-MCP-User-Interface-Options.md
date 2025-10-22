# WordPress MCP User Interface Options

This document outlines different approaches to provide a user-friendly interface for WordPress management using the AIWU MCP integration with Kiro IDE.

## Background

- User wants to manage WordPress site without pro versions of Claude or other AI tools
- AIWU MCP integration is working with Kiro IDE
- Need user-friendly interface for non-technical users
- 36 WordPress functions available through MCP

---

## Option 1: Kiro Agent Hooks ⭐ **RECOMMENDED**

### Description
Create automated workflows within Kiro that trigger on user actions (button clicks, file saves, etc.).

### Implementation
```yaml
Hook Examples:
- "Quick Blog Post" - Form interface for creating posts
- "Publish Draft" - One-click publishing of draft posts  
- "Bulk Image Upload" - Drag & drop media management
- "SEO Optimizer" - Auto-generate meta descriptions
- "Content Scheduler" - Schedule posts for future publication
```

### Sample Hook Workflow
```
Hook Name: "Quick Blog Post"
Trigger: Manual button click
User Interface: Form with fields for:
  - Post Title
  - Post Content (Markdown supported)
  - Categories/Tags
  - Featured Image URL
  - Publish Status

Actions:
1. Prompt user for post details
2. Call wp_create_post with form data
3. Call wp_set_featured_image if image provided
4. Call wp_add_post_terms for categories
5. Show success message with post URL
```

### Pros
- ✅ **No additional setup** - Works entirely within Kiro
- ✅ **User-friendly** - Simple button clicks and forms
- ✅ **Automated workflows** - Can chain multiple WordPress operations
- ✅ **Highly customizable** - Easy to modify for specific needs
- ✅ **No coding required** - Visual hook builder in Kiro
- ✅ **Integrated experience** - Seamless with existing Kiro workflow

### Cons
- ❌ **Limited to Kiro environment** - User must use Kiro IDE
- ❌ **Learning curve** - User needs to understand Kiro hooks concept

### Setup Complexity
**Low** - Use Kiro's built-in hook UI or command palette "Open Kiro Hook UI"

### Best For
- Users comfortable with Kiro IDE
- Workflow automation needs
- Integration with existing development processes

---

## Option 2: Simple Web Interface

### Description
Create a lightweight HTML/JavaScript interface that communicates with the MCP bridge server.

### Implementation
```html
<!-- wordpress-manager.html -->
<!DOCTYPE html>
<html>
<head>
    <title>WordPress Manager</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px; 
        }
        .form-group { margin-bottom: 15px; }
        label { 
            display: block; 
            margin-bottom: 5px; 
            font-weight: bold; 
        }
        input, textarea, select { 
            width: 100%; 
            padding: 8px; 
            border: 1px solid #ddd; 
            border-radius: 4px; 
        }
        textarea { height: 200px; }
        button { 
            background: #0073aa; 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer; 
        }
        button:hover { background: #005a87; }
        .posts-list { margin-top: 30px; }
        .post-item { 
            border: 1px solid #ddd; 
            padding: 15px; 
            margin-bottom: 10px; 
            border-radius: 4px; 
        }
        .status-draft { border-left: 4px solid #f39c12; }
        .status-publish { border-left: 4px solid #27ae60; }
    </style>
</head>
<body>
    <h1>WordPress Manager</h1>
    
    <!-- Create Post Section -->
    <div class="form-group">
        <h2>Create New Post</h2>
        <label>Title:</label>
        <input type="text" id="postTitle" placeholder="Enter post title">
        
        <label>Content:</label>
        <textarea id="postContent" placeholder="Enter post content (Markdown supported)"></textarea>
        
        <label>Excerpt:</label>
        <textarea id="postExcerpt" placeholder="Optional post excerpt" style="height: 80px;"></textarea>
        
        <label>Status:</label>
        <select id="postStatus">
            <option value="draft">Draft</option>
            <option value="publish">Publish Immediately</option>
        </select>
        
        <label>Featured Image URL:</label>
        <input type="url" id="featuredImage" placeholder="https://example.com/image.jpg">
        
        <button onclick="createPost()">Create Post</button>
    </div>
    
    <!-- Manage Posts Section -->
    <div class="form-group">
        <h2>Manage Posts</h2>
        <button onclick="loadPosts()">Refresh Posts</button>
        <button onclick="loadDrafts()">Show Drafts Only</button>
        <div id="postsList" class="posts-list"></div>
    </div>

    <!-- Media Management Section -->
    <div class="form-group">
        <h2>Media Management</h2>
        <label>Upload Image from URL:</label>
        <input type="url" id="mediaUrl" placeholder="https://example.com/image.jpg">
        <input type="text" id="mediaTitle" placeholder="Image title">
        <button onclick="uploadMedia()">Upload to Media Library</button>
    </div>

    <!-- Site Info Section -->
    <div class="form-group">
        <h2>Site Information</h2>
        <button onclick="getSiteInfo()">Get Site Info</button>
        <button onclick="listPlugins()">List Plugins</button>
        <div id="siteInfo"></div>
    </div>

    <script>
        // WordPress Management Functions
        function createPost() {
            const title = document.getElementById('postTitle').value;
            const content = document.getElementById('postContent').value;
            const excerpt = document.getElementById('postExcerpt').value;
            const status = document.getElementById('postStatus').value;
            const featuredImage = document.getElementById('featuredImage').value;
            
            if (!title || !content) {
                alert('Please fill in title and content');
                return;
            }
            
            // Call MCP bridge via fetch to local server
            callWordPressAPI('wp_create_post', {
                post_title: title,
                post_content: content,
                post_excerpt: excerpt,
                post_status: status
            }).then(result => {
                alert('Post created successfully!');
                clearForm();
                loadPosts();
            }).catch(error => {
                alert('Error creating post: ' + error.message);
            });
        }
        
        function loadPosts() {
            callWordPressAPI('wp_get_posts', { limit: 20 })
                .then(posts => {
                    displayPosts(posts);
                })
                .catch(error => {
                    document.getElementById('postsList').innerHTML = 
                        '<p>Error loading posts: ' + error.message + '</p>';
                });
        }
        
        function loadDrafts() {
            callWordPressAPI('wp_get_posts', { 
                limit: 20, 
                post_status: 'draft' 
            }).then(posts => {
                displayPosts(posts);
            });
        }
        
        function uploadMedia() {
            const url = document.getElementById('mediaUrl').value;
            const title = document.getElementById('mediaTitle').value;
            
            if (!url) {
                alert('Please enter image URL');
                return;
            }
            
            callWordPressAPI('wp_upload_media', {
                url: url,
                title: title
            }).then(result => {
                alert('Image uploaded successfully!');
                document.getElementById('mediaUrl').value = '';
                document.getElementById('mediaTitle').value = '';
            });
        }
        
        function getSiteInfo() {
            callWordPressAPI('mcp_ping')
                .then(info => {
                    document.getElementById('siteInfo').innerHTML = 
                        `<p><strong>Site:</strong> ${info.name}</p>
                         <p><strong>Time:</strong> ${info.time}</p>`;
                });
        }
        
        function listPlugins() {
            callWordPressAPI('wp_list_plugins')
                .then(plugins => {
                    let html = '<h3>Installed Plugins:</h3><ul>';
                    plugins.forEach(plugin => {
                        html += `<li>${plugin.Name} (v${plugin.Version})</li>`;
                    });
                    html += '</ul>';
                    document.getElementById('siteInfo').innerHTML = html;
                });
        }
        
        function displayPosts(posts) {
            let html = '';
            posts.forEach(post => {
                html += `
                    <div class="post-item status-${post.post_status}">
                        <h3>${post.post_title}</h3>
                        <p><strong>Status:</strong> ${post.post_status}</p>
                        <p><strong>Excerpt:</strong> ${post.post_excerpt || 'No excerpt'}</p>
                        <p><strong>URL:</strong> <a href="${post.permalink}" target="_blank">${post.permalink}</a></p>
                        <button onclick="editPost(${post.ID})">Edit</button>
                        ${post.post_status === 'draft' ? 
                            `<button onclick="publishPost(${post.ID})">Publish</button>` : ''}
                        <button onclick="deletePost(${post.ID})" style="background: #e74c3c;">Delete</button>
                    </div>
                `;
            });
            document.getElementById('postsList').innerHTML = html;
        }
        
        function publishPost(postId) {
            if (confirm('Publish this post?')) {
                callWordPressAPI('wp_update_post', {
                    ID: postId,
                    fields: { post_status: 'publish' }
                }).then(() => {
                    alert('Post published!');
                    loadPosts();
                });
            }
        }
        
        function deletePost(postId) {
            if (confirm('Are you sure you want to delete this post?')) {
                callWordPressAPI('wp_delete_post', {
                    ID: postId,
                    force: true
                }).then(() => {
                    alert('Post deleted!');
                    loadPosts();
                });
            }
        }
        
        function clearForm() {
            document.getElementById('postTitle').value = '';
            document.getElementById('postContent').value = '';
            document.getElementById('postExcerpt').value = '';
            document.getElementById('postStatus').value = 'draft';
            document.getElementById('featuredImage').value = '';
        }
        
        // API Communication Function
        async function callWordPressAPI(method, params = {}) {
            // This would need to communicate with your MCP bridge
            // Implementation depends on how you expose the bridge
            const response = await fetch('/api/wordpress', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    method: method,
                    params: params
                })
            });
            
            if (!response.ok) {
                throw new Error('API call failed');
            }
            
            return await response.json();
        }
        
        // Load posts on page load
        window.onload = function() {
            loadPosts();
        };
    </script>
</body>
</html>
```

### Additional Backend Bridge
```python
# web_bridge_server.py
from flask import Flask, request, jsonify, render_template
import subprocess
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('wordpress-manager.html')

@app.route('/api/wordpress', methods=['POST'])
def wordpress_api():
    data = request.json
    method = data.get('method')
    params = data.get('params', {})
    
    # Call your MCP bridge
    mcp_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": method,
            "arguments": params
        }
    }
    
    # Execute via your existing MCP bridge
    result = subprocess.run([
        'python', 'wordpress_mcp_server.py'
    ], input=json.dumps(mcp_request), 
       capture_output=True, text=True)
    
    if result.returncode == 0:
        response = json.loads(result.stdout)
        return jsonify(response.get('result', {}))
    else:
        return jsonify({'error': 'MCP call failed'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### Pros
- ✅ **Familiar interface** - Standard web UI that anyone can use
- ✅ **Standalone application** - Doesn't require Kiro to be open
- ✅ **Mobile friendly** - Can be made responsive
- ✅ **Customizable design** - Full control over appearance
- ✅ **Multi-user capable** - Can be hosted for team access

### Cons
- ❌ **Additional development** - Requires HTML/CSS/JavaScript skills
- ❌ **Separate server needed** - Need to run web server alongside MCP bridge
- ❌ **Security considerations** - Need to handle authentication/authorization
- ❌ **Maintenance overhead** - Another application to maintain

### Setup Complexity
**Medium** - Requires web development and server setup

### Best For
- Users who prefer web interfaces
- Teams needing shared access
- Mobile/tablet usage scenarios

---

## Option 3: Kiro Steering Rules

### Description
Create steering files that give users simple natural language commands for WordPress management.

### Implementation
```markdown
<!-- .kiro/steering/wordpress-commands.md -->
---
inclusion: manual
---

# WordPress Management Commands

Use these simple commands to manage your WordPress site:

## Post Management Commands
- **"create post [title]"** - Creates a new draft post with the specified title
- **"publish post [ID]"** - Publishes a draft post by ID number
- **"list my posts"** - Shows all posts with titles, status, and URLs
- **"list drafts"** - Shows only draft posts
- **"update post [ID] with [content]"** - Updates post content
- **"delete post [ID]"** - Deletes a post (will ask for confirmation)
- **"get post [ID]"** - Shows full details of a specific post

## Content Creation Commands
- **"write blog post about [topic]"** - Creates a draft post with AI-generated content
- **"create page [title]"** - Creates a new WordPress page
- **"add excerpt to post [ID]: [excerpt]"** - Adds excerpt to existing post

## Media Management Commands
- **"upload image from [URL]"** - Adds image to media library from URL
- **"set featured image [media_ID] for post [post_ID]"** - Sets post thumbnail
- **"list media files"** - Shows recent media library uploads
- **"generate AI image: [description]"** - Creates AI image and uploads to media library

## Site Management Commands
- **"list plugins"** - Shows all installed WordPress plugins
- **"get site info"** - Shows WordPress site details and status
- **"list users"** - Shows WordPress user accounts
- **"check site health"** - Runs basic site diagnostics

## Category and Tag Commands
- **"list categories"** - Shows all post categories
- **"create category [name]"** - Creates a new post category
- **"add post [ID] to category [name]"** - Assigns category to post
- **"list tags"** - Shows all post tags

## Advanced Commands
- **"backup post [ID]"** - Creates a backup copy of post content
- **"schedule post [ID] for [date/time]"** - Schedules post for future publication
- **"optimize post [ID] for SEO"** - Analyzes and improves post SEO
- **"convert draft [ID] to page"** - Converts a draft post to a page

## Batch Operations
- **"publish all drafts"** - Publishes all draft posts (with confirmation)
- **"list posts from last week"** - Shows recent posts
- **"backup all posts"** - Creates backup of all post content

## Examples
```
User: "create post How to Use WordPress MCP"
Kiro: Creates a new draft post with that title

User: "list my posts"  
Kiro: Shows all posts with IDs, titles, and status

User: "publish post 5"
Kiro: Changes post #5 from draft to published

User: "upload image from https://example.com/photo.jpg"
Kiro: Downloads and adds image to WordPress media library
```

## Command Format Rules
- Use square brackets [ID] for post/media ID numbers
- Use quotes for multi-word titles: "My Blog Post Title"
- Commands are case-insensitive
- Kiro will ask for confirmation on destructive operations
```

### Additional Steering File for Workflows
```markdown
<!-- .kiro/steering/wordpress-workflows.md -->
---
inclusion: manual
---

# WordPress Content Workflows

## Blog Post Creation Workflow
When user says "create blog post workflow":
1. Ask for post title
2. Ask for main topic/keywords
3. Generate post content using AI
4. Create draft post in WordPress
5. Ask if they want to add featured image
6. If yes, generate AI image based on topic
7. Set featured image for the post
8. Ask if ready to publish or keep as draft

## Content Update Workflow  
When user says "update content workflow":
1. List all draft posts
2. Ask which post to update
3. Show current content
4. Ask what changes to make
5. Update the post
6. Ask if ready to publish

## SEO Optimization Workflow
When user says "optimize for SEO":
1. Ask for post ID or show list of posts
2. Analyze current post content
3. Suggest title improvements
4. Generate meta description
5. Suggest categories/tags
6. Update post with improvements
```

### Pros
- ✅ **Natural language** - Users type commands in plain English
- ✅ **No UI to learn** - Just chat with Kiro normally
- ✅ **Flexible commands** - Easy to add new command patterns
- ✅ **Context aware** - Can reference previous commands/posts
- ✅ **Minimal setup** - Just create markdown files

### Cons
- ❌ **Command memorization** - Users need to remember command syntax
- ❌ **Text-only interface** - No visual forms or buttons
- ❌ **Limited discoverability** - Hard to know what commands exist
- ❌ **Requires Kiro** - Must use Kiro IDE for all operations

### Setup Complexity
**Low** - Just create steering markdown files

### Best For
- Users comfortable with command-line interfaces
- Power users who prefer keyboard over mouse
- Integration with existing Kiro workflows

---

## Option 4: Custom Kiro Extension

### Description
Build a dedicated Kiro extension with custom UI components, forms, and WordPress-specific features.

### Implementation
```javascript
// wordpress-manager-extension.js
class WordPressManagerExtension {
    constructor() {
        this.panel = null;
        this.posts = [];
    }
    
    // Extension initialization
    activate() {
        this.createPanel();
        this.loadPosts();
    }
    
    // Create main UI panel
    createPanel() {
        this.panel = kiro.ui.createPanel({
            title: 'WordPress Manager',
            icon: 'wordpress',
            position: 'sidebar'
        });
        
        this.panel.setContent(this.renderMainUI());
    }
    
    // Main UI template
    renderMainUI() {
        return `
            <div class="wp-manager">
                <div class="wp-section">
                    <h3>Quick Actions</h3>
                    <button class="wp-btn primary" onclick="wpManager.showCreatePost()">
                        📝 New Post
                    </button>
                    <button class="wp-btn" onclick="wpManager.showDrafts()">
                        📄 View Drafts
                    </button>
                    <button class="wp-btn" onclick="wpManager.showMedia()">
                        🖼️ Media Library
                    </button>
                </div>
                
                <div class="wp-section">
                    <h3>Recent Posts</h3>
                    <div id="wp-posts-list">
                        Loading posts...
                    </div>
                </div>
                
                <div class="wp-section">
                    <h3>Site Status</h3>
                    <div id="wp-site-status">
                        <button onclick="wpManager.checkSiteHealth()">
                            🔍 Check Site Health
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Create post form
    showCreatePost() {
        const modal = kiro.ui.createModal({
            title: 'Create New Post',
            width: 600,
            height: 500
        });
        
        modal.setContent(`
            <form id="wp-create-form" class="wp-form">
                <div class="form-group">
                    <label>Post Title</label>
                    <input type="text" id="wp-title" required>
                </div>
                
                <div class="form-group">
                    <label>Content</label>
                    <textarea id="wp-content" rows="10" placeholder="Write your post content here..."></textarea>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label>Status</label>
                        <select id="wp-status">
                            <option value="draft">Draft</option>
                            <option value="publish">Publish</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Post Type</label>
                        <select id="wp-type">
                            <option value="post">Blog Post</option>
                            <option value="page">Page</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Featured Image URL (optional)</label>
                    <input type="url" id="wp-featured-image">
                </div>
                
                <div class="form-actions">
                    <button type="button" onclick="wpManager.createPost()" class="wp-btn primary">
                        Create Post
                    </button>
                    <button type="button" onclick="kiro.ui.closeModal()" class="wp-btn secondary">
                        Cancel
                    </button>
                </div>
            </form>
        `);
        
        modal.show();
    }
    
    // Create post via MCP
    async createPost() {
        const title = document.getElementById('wp-title').value;
        const content = document.getElementById('wp-content').value;
        const status = document.getElementById('wp-status').value;
        const postType = document.getElementById('wp-type').value;
        const featuredImage = document.getElementById('wp-featured-image').value;
        
        if (!title || !content) {
            kiro.ui.showNotification('Please fill in title and content', 'error');
            return;
        }
        
        try {
            // Call WordPress MCP function
            const result = await kiro.mcp.call('wp_create_post', {
                post_title: title,
                post_content: content,
                post_status: status,
                post_type: postType
            });
            
            // Set featured image if provided
            if (featuredImage && result.ID) {
                const media = await kiro.mcp.call('wp_upload_media', {
                    url: featuredImage,
                    title: title + ' - Featured Image'
                });
                
                if (media.id) {
                    await kiro.mcp.call('wp_set_featured_image', {
                        post_id: result.ID,
                        media_id: media.id
                    });
                }
            }
            
            kiro.ui.showNotification('Post created successfully!', 'success');
            kiro.ui.closeModal();
            this.loadPosts(); // Refresh posts list
            
        } catch (error) {
            kiro.ui.showNotification('Error creating post: ' + error.message, 'error');
        }
    }
    
    // Load and display posts
    async loadPosts() {
        try {
            const posts = await kiro.mcp.call('wp_get_posts', { limit: 10 });
            this.posts = posts;
            this.renderPostsList();
        } catch (error) {
            document.getElementById('wp-posts-list').innerHTML = 
                '<p class="error">Error loading posts: ' + error.message + '</p>';
        }
    }
    
    // Render posts list
    renderPostsList() {
        const container = document.getElementById('wp-posts-list');
        if (!container) return;
        
        let html = '';
        this.posts.forEach(post => {
            html += `
                <div class="wp-post-item ${post.post_status}">
                    <div class="post-title">${post.post_title}</div>
                    <div class="post-meta">
                        <span class="status">${post.post_status}</span>
                        <span class="id">ID: ${post.ID}</span>
                    </div>
                    <div class="post-actions">
                        <button onclick="wpManager.editPost(${post.ID})" class="wp-btn small">Edit</button>
                        <button onclick="wpManager.viewPost('${post.permalink}')" class="wp-btn small">View</button>
                        ${post.post_status === 'draft' ? 
                            `<button onclick="wpManager.publishPost(${post.ID})" class="wp-btn small primary">Publish</button>` : ''}
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html || '<p>No posts found</p>';
    }
    
    // Publish draft post
    async publishPost(postId) {
        if (!confirm('Publish this post?')) return;
        
        try {
            await kiro.mcp.call('wp_update_post', {
                ID: postId,
                fields: { post_status: 'publish' }
            });
            
            kiro.ui.showNotification('Post published successfully!', 'success');
            this.loadPosts();
        } catch (error) {
            kiro.ui.showNotification('Error publishing post: ' + error.message, 'error');
        }
    }
    
    // Show drafts only
    async showDrafts() {
        try {
            const drafts = await kiro.mcp.call('wp_get_posts', { 
                post_status: 'draft',
                limit: 20 
            });
            
            // Create drafts modal
            const modal = kiro.ui.createModal({
                title: 'Draft Posts',
                width: 700,
                height: 600
            });
            
            let html = '<div class="wp-drafts-list">';
            drafts.forEach(draft => {
                html += `
                    <div class="wp-draft-item">
                        <h4>${draft.post_title}</h4>
                        <p>${draft.post_excerpt || 'No excerpt'}</p>
                        <div class="draft-actions">
                            <button onclick="wpManager.editPost(${draft.ID})" class="wp-btn">Edit</button>
                            <button onclick="wpManager.publishPost(${draft.ID})" class="wp-btn primary">Publish</button>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            
            modal.setContent(html);
            modal.show();
            
        } catch (error) {
            kiro.ui.showNotification('Error loading drafts: ' + error.message, 'error');
        }
    }
    
    // Check site health
    async checkSiteHealth() {
        try {
            const ping = await kiro.mcp.call('mcp_ping');
            const plugins = await kiro.mcp.call('wp_list_plugins');
            const postCount = await kiro.mcp.call('wp_count_posts');
            
            const statusHtml = `
                <div class="site-health">
                    <h4>✅ Site Status: Online</h4>
                    <p><strong>Site Name:</strong> ${ping.name}</p>
                    <p><strong>Last Check:</strong> ${ping.time}</p>
                    <p><strong>Active Plugins:</strong> ${plugins.length}</p>
                    <p><strong>Published Posts:</strong> ${postCount.publish || 0}</p>
                    <p><strong>Draft Posts:</strong> ${postCount.draft || 0}</p>
                </div>
            `;
            
            document.getElementById('wp-site-status').innerHTML = statusHtml;
            
        } catch (error) {
            document.getElementById('wp-site-status').innerHTML = 
                '<div class="site-health error">❌ Site connection failed: ' + error.message + '</div>';
        }
    }
}

// CSS Styles
const wpStyles = `
    .wp-manager {
        padding: 15px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .wp-section {
        margin-bottom: 25px;
        padding-bottom: 15px;
        border-bottom: 1px solid #eee;
    }
    
    .wp-section h3 {
        margin: 0 0 10px 0;
        color: #333;
        font-size: 14px;
        font-weight: 600;
    }
    
    .wp-btn {
        background: #f1f1f1;
        border: 1px solid #ddd;
        padding: 8px 12px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    
    .wp-btn.primary {
        background: #0073aa;
        color: white;
        border-color: #0073aa;
    }
    
    .wp-btn.small {
        padding: 4px 8px;
        font-size: 11px;
    }
    
    .wp-post-item {
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    
    .wp-post-item.draft {
        border-left: 4px solid #f39c12;
    }
    
    .wp-post-item.publish {
        border-left: 4px solid #27ae60;
    }
    
    .post-title {
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    .post-meta {
        font-size: 11px;
        color: #666;
        margin-bottom: 8px;
    }
    
    .wp-form .form-group {
        margin-bottom: 15px;
    }
    
    .wp-form label {
        display: block;
        margin-bottom: 5px;
        font-weight: 600;
        font-size: 12px;
    }
    
    .wp-form input, .wp-form textarea, .wp-form select {
        width: 100%;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 13px;
    }
    
    .form-row {
        display: flex;
        gap: 15px;
    }
    
    .form-actions {
        margin-top: 20px;
        text-align: right;
    }
`;

// Initialize extension
const wpManager = new WordPressManagerExtension();

// Register with Kiro
kiro.extensions.register('wordpress-manager', {
    name: 'WordPress Manager',
    version: '1.0.0',
    activate: () => wpManager.activate(),
    styles: wpStyles
});
```

### Extension Package Structure
```
wordpress-manager-extension/
├── manifest.json
├── main.js
├── styles.css
├── icons/
│   └── wordpress.svg
└── README.md
```

### Pros
- ✅ **Native Kiro integration** - Seamless UI within Kiro IDE
- ✅ **Rich UI components** - Forms, modals, buttons, lists
- ✅ **Professional appearance** - Matches Kiro's design system
- ✅ **Full feature access** - Can use all Kiro APIs and MCP functions
- ✅ **Extensible** - Easy to add new features and workflows

### Cons
- ❌ **High development complexity** - Requires JavaScript/Kiro API knowledge
- ❌ **Kiro-specific** - Only works within Kiro IDE
- ❌ **Extension maintenance** - Need to update for Kiro API changes
- ❌ **Distribution complexity** - Need to package and distribute extension

### Setup Complexity
**High** - Requires extension development skills and Kiro API knowledge

### Best For
- Professional WordPress management workflows
- Teams already using Kiro IDE extensively
- Users needing advanced WordPress features

---

## Comparison Matrix

| Feature | Kiro Hooks | Web Interface | Steering Rules | Kiro Extension |
|---------|------------|---------------|----------------|----------------|
| **Setup Complexity** | Low | Medium | Low | High |
| **User Friendliness** | High | High | Medium | High |
| **Customization** | High | High | Medium | Very High |
| **Standalone Usage** | No | Yes | No | No |
| **Mobile Support** | No | Yes | No | No |
| **Development Skills** | None | Web Dev | None | Advanced |
| **Maintenance** | Low | Medium | Low | High |
| **Multi-user** | No | Yes | No | No |

---

## Recommendations by User Type

### **Non-Technical Users**
**Recommended: Option 1 (Kiro Hooks)**
- Simple button-click interface
- No coding required
- Built into Kiro IDE

### **Teams/Multiple Users**
**Recommended: Option 2 (Web Interface)**
- Accessible from any device
- Can be hosted for team access
- Familiar web UI

### **Power Users**
**Recommended: Option 3 (Steering Rules)**
- Fast command-based workflow
- Natural language interface
- Highly efficient for frequent use

### **Professional/Enterprise**
**Recommended: Option 4 (Kiro Extension)**
- Full-featured WordPress management
- Professional UI/UX
- Extensible for custom workflows

---

## Implementation Timeline

### Phase 1: Quick Start (1-2 days)
- Implement Option 1 (Kiro Hooks) for basic post creation
- Create 3-5 essential hooks for common tasks

### Phase 2: Enhanced Interface (1 week)
- Add Option 3 (Steering Rules) for power users
- Create comprehensive command library

### Phase 3: Advanced Features (2-3 weeks)
- Implement Option 2 (Web Interface) for broader access
- Add media management and advanced workflows

### Phase 4: Professional Solution (1 month)
- Develop Option 4 (Kiro Extension) for full-featured management
- Include analytics, SEO tools, and automation

---

## Cost Considerations

| Option | Development Cost | Maintenance Cost | Hosting Cost |
|--------|------------------|------------------|--------------|
| Kiro Hooks | Very Low | Very Low | None |
| Web Interface | Medium | Medium | Low-Medium |
| Steering Rules | Very Low | Very Low | None |
| Kiro Extension | High | Medium | None |

---

## Next Steps

1. **Evaluate user technical comfort level**
2. **Determine primary use cases** (blogging, content management, etc.)
3. **Consider team vs. individual usage**
4. **Choose implementation approach** based on requirements
5. **Start with simplest viable option** and iterate

Each option can be implemented incrementally, allowing you to start simple and add complexity as needed.