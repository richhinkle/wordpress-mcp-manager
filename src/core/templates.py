"""
HTML templates for the WordPress MCP Manager
"""

WEB_INTERFACE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram to WordPress Manager</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .hero {
            background: white;
            padding: 40px;
            border-radius: 16px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .hero h1 {
            color: #333;
            margin-bottom: 15px;
            font-size: 3em;
            background: linear-gradient(45deg, #E1306C, #F56040, #F77737, #FCAF45, #FFDC80);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .hero p {
            color: #666;
            font-size: 1.3em;
            margin-bottom: 20px;
        }
        
        .workflow {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            margin: 30px 0;
            flex-wrap: wrap;
        }
        
        .workflow-step {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            min-width: 150px;
        }
        
        .workflow-step .icon {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .workflow-arrow {
            font-size: 2em;
            color: #666;
        }
        
        .status {
            margin-top: 20px;
            padding: 12px 24px;
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
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .instagram-viewer {
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .viewer-header {
            background: linear-gradient(45deg, #E1306C, #F56040);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .viewer-header h2 {
            margin: 0;
            font-size: 1.5em;
        }
        
        .post-display {
            padding: 0;
            min-height: 600px;
            display: flex;
            flex-direction: column;
        }
        
        .post-image {
            width: 100%;
            max-height: 500px;
            object-fit: cover;
            background: #f8f9fa;
        }
        
        .post-content {
            padding: 20px;
            flex: 1;
        }
        
        .post-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            font-size: 0.9em;
            color: #666;
        }
        
        .post-caption {
            line-height: 1.6;
            margin-bottom: 15px;
        }
        
        .post-hashtags {
            color: #1877f2;
            margin-bottom: 15px;
        }
        
        .post-actions {
            display: flex;
            gap: 10px;
            padding: 20px;
            border-top: 1px solid #eee;
        }
        
        .post-navigation {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            background: #f8f9fa;
            border-top: 1px solid #eee;
        }
        
        .nav-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s ease;
        }
        
        .nav-btn:hover:not(:disabled) {
            background: #5a6fd8;
        }
        
        .nav-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .post-counter {
            font-weight: 600;
            color: #333;
        }
        
        .chat-panel {
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            height: 700px;
        }
        
        .chat-header {
            background: #667eea;
            color: white;
            padding: 20px;
            border-radius: 16px 16px 0 0;
            text-align: center;
        }
        
        .chat-header h2 {
            margin: 0;
            font-size: 1.3em;
        }
        
        .chat-container {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        .chat-input-area {
            padding: 20px;
            border-top: 1px solid #eee;
            background: white;
            border-radius: 0 0 16px 16px;
        }
        
        .chat-input-group {
            display: flex;
            gap: 10px;
        }
        
        .chat-input {
            flex: 1;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s ease;
        }
        
        .chat-input:focus {
            border-color: #667eea;
        }
        
        .send-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.3s ease;
        }
        
        .send-btn:hover {
            background: #5a6fd8;
        }
        
        .quick-actions {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        
        .quick-action {
            background: #e9ecef;
            border: none;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 12px;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        
        .quick-action:hover {
            background: #dee2e6;
        }
        
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        
        .btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        .btn.success {
            background: #28a745;
        }
        
        .btn.success:hover {
            background: #218838;
        }
        
        .btn.danger {
            background: #dc3545;
        }
        
        .btn.danger:hover {
            background: #c82333;
        }
        
        .btn.secondary {
            background: #6c757d;
        }
        
        .btn.secondary:hover {
            background: #5a6268;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }
        
        .empty-state .icon {
            font-size: 4em;
            margin-bottom: 20px;
            opacity: 0.5;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .chat-message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 85%;
        }
        
        .chat-message.user {
            background: #667eea;
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 4px;
        }
        
        .chat-message.assistant {
            background: white;
            border: 1px solid #e1e5e9;
            border-bottom-left-radius: 4px;
        }
        
        .chat-message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .chat-actions {
            margin-top: 10px;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .chat-action-btn {
            background: #e9ecef;
            border: 1px solid #dee2e6;
            padding: 6px 12px;
            border-radius: 16px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .chat-action-btn:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 1000;
            transform: translateX(400px);
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
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .workflow {
                flex-direction: column;
            }
            
            .workflow-arrow {
                transform: rotate(90deg);
            }
            
            .hero h1 {
                font-size: 2em;
            }
            
            .chat-panel {
                height: 500px;
            }
        }
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
        <!-- Hero Section -->
        <div class="hero">
            <h1>📸 Instagram → WordPress</h1>
            <p>Transform your Instagram content into WordPress posts with AI-powered chat</p>
            
            <div class="workflow">
                <div class="workflow-step">
                    <div class="icon">📱</div>
                    <div>Chat Command</div>
                    <small>"scrape @username"</small>
                </div>
                <div class="workflow-arrow">→</div>
                <div class="workflow-step">
                    <div class="icon">🔍</div>
                    <div>Apify Scrapes</div>
                    <small>Professional API</small>
                </div>
                <div class="workflow-arrow">→</div>
                <div class="workflow-step">
                    <div class="icon">👁️</div>
                    <div>Preview Posts</div>
                    <small>Browse & Select</small>
                </div>
                <div class="workflow-arrow">→</div>
                <div class="workflow-step">
                    <div class="icon">📝</div>
                    <div>WordPress</div>
                    <small>One-click import</small>
                </div>
            </div>
            
            <div id="connection-status" class="status">Checking connection...</div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content">
            <!-- Instagram Post Viewer -->
            <div class="instagram-viewer">
                <div class="viewer-header">
                    <h2>📸 Instagram Posts</h2>
                </div>
                
                <div class="post-display" id="post-display">
                    <div class="empty-state">
                        <div class="icon">📱</div>
                        <h3>Ready to Import Instagram Posts</h3>
                        <p>Use the chat to scrape Instagram posts:</p>
                        <div style="margin: 20px 0;">
                            <code style="background: #f8f9fa; padding: 8px 12px; border-radius: 6px; font-size: 14px;">
                                scrape instagram @cardmyyard_oviedo
                            </code>
                        </div>
                        <p>Posts will appear here for preview and import</p>
                    </div>
                </div>
            </div>
            
            <!-- Chat Panel -->
            <div class="chat-panel">
                <div class="chat-header">
                    <h2>🤖 AI Assistant</h2>
                </div>
                
                <div class="chat-container" id="chat-container">
                    <div class="chat-message assistant">
                        <strong>🤖 Assistant:</strong> Hi! I'm your Instagram-to-WordPress assistant. Here's what I can do:
                        <div class="chat-actions">
                            <button class="chat-action-btn" onclick="executeChatAction('scrape instagram @cardmyyard_oviedo')">📱 Scrape @cardmyyard_oviedo</button>
                            <button class="chat-action-btn" onclick="executeChatAction('apify status')">🔍 Check Apify Status</button>
                            <button class="chat-action-btn" onclick="executeChatAction('help')">❓ Show All Commands</button>
                        </div>
                    </div>
                </div>
                
                <div class="chat-input-area">
                    <div class="quick-actions">
                        <button class="quick-action" onclick="executeChatAction('scrape instagram @cardmyyard_oviedo')">Scrape @cardmyyard_oviedo</button>
                        <button class="quick-action" onclick="executeChatAction('bulk import @cardmyyard_oviedo')">Bulk Import</button>
                        <button class="quick-action" onclick="executeChatAction('cache stats')">Cache Stats</button>
                        <button class="quick-action" onclick="executeChatAction('list posts')">List Posts</button>
                    </div>
                    
                    <div class="chat-input-group">
                        <input type="text" id="chat-input" class="chat-input" placeholder="Try: 'scrape instagram @username' or 'bulk import @username'" />
                        <button class="send-btn" onclick="sendChatMessage()">Send</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="/static/app.js?v=2"></script>
</body>
</html>
'''