"""
HTML templates for the WordPress MCP Manager
"""

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
        
        /* Chat Interface Styles */
        .chat-message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
            line-height: 1.4;
        }
        
        .chat-message.user {
            background: #e3f2fd;
            margin-left: 20px;
            border-left: 4px solid #2196f3;
        }
        
        .chat-message.assistant {
            background: #f1f8e9;
            margin-right: 20px;
            border-left: 4px solid #4caf50;
        }
        
        .chat-message.error {
            background: #ffebee;
            border-left: 4px solid #f44336;
        }
        
        .chat-suggestions {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
            margin-top: 10px;
        }
        
        .suggestion-btn {
            background: #f0f0f0;
            border: 1px solid #ddd;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .suggestion-btn:hover {
            background: #e0e0e0;
        }
        
        .chat-actions {
            margin-top: 8px;
        }
        
        .chat-action-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
            margin-right: 5px;
            margin-bottom: 5px;
        }
        
        .chat-action-btn:hover {
            background: #5a6fd8;
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
                
                <div style="margin-top: 30px;">
                    <h3>📷 Upload from URL</h3>
                    <div class="form-group">
                        <input type="url" id="media-url" placeholder="https://example.com/image.jpg">
                    </div>
                    <div class="form-group">
                        <input type="text" id="media-title" placeholder="Image title (optional)">
                    </div>
                    <button class="btn success" onclick="uploadFromUrl()">Upload Media</button>
                </div>
            </div>
        </div>
        
        <!-- AI Chat Interface -->
        <div class="card" style="margin-bottom: 30px;">
            <h2>🤖 AI Assistant</h2>
            <div id="chat-container" style="height: 300px; overflow-y: auto; border: 2px solid #e1e5e9; border-radius: 8px; padding: 15px; margin-bottom: 15px; background: #f8f9fa;">
                <div class="chat-message assistant">
                    <strong>🤖 Assistant:</strong> Hi! I'm your WordPress AI assistant. I can help you manage posts, generate content, upload images, and more. Try asking me something like "list my posts" or "create a new post"!
                </div>
            </div>
            <div style="display: flex; gap: 10px;">
                <input type="text" id="chat-input" placeholder="Ask me anything about your WordPress site..." 
                       style="flex: 1; padding: 12px; border: 2px solid #e1e5e9; border-radius: 8px;">
                <button class="btn" onclick="sendChatMessage()">Send</button>
            </div>
            <div id="chat-suggestions" style="margin-top: 10px; display: flex; gap: 5px; flex-wrap: wrap;"></div>
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

    <script src="/static/app.js"></script>
</body>
</html>
'''