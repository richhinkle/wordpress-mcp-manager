// WordPress Manager Frontend JavaScript

// Application state
let currentPosts = [];

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    checkConnection();
    loadPosts();
    
    // Form submission (if form exists)
    const createPostForm = document.getElementById('create-post-form');
    if (createPostForm) {
        createPostForm.addEventListener('submit', function(e) {
            e.preventDefault();
            createPost();
        });
    }
    
    // Search on Enter key (if search input exists)
    const searchPostsInput = document.getElementById('search-posts');
    if (searchPostsInput) {
        searchPostsInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchPosts();
            }
        });
    }
    
    // Chat input on Enter key (if chat input exists)
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });
    }
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
    const statusEl = document.getElementById('connection-status');
    if (!statusEl) {
        console.log('Connection status element not found - skipping connection check');
        return;
    }
    
    try {
        const result = await apiCall('/api/health');
        
        if (result.wordpress_connected) {
            statusEl.textContent = `✅ Connected to ${result.site_name || 'WordPress'}`;
            statusEl.className = 'status connected';
        } else {
            statusEl.textContent = '❌ WordPress connection failed';
            statusEl.className = 'status disconnected';
        }
    } catch (error) {
        statusEl.textContent = '⚠️ Connection check failed';
        statusEl.className = 'status disconnected';
        console.log('Connection check failed (this is normal if WordPress credentials need updating):', error.message);
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
    const postsContainer = document.getElementById('posts-container');
    if (!postsContainer) {
        console.log('Posts container not found - skipping loadPosts');
        return;
    }
    
    try {
        postsContainer.innerHTML = '<div class="loading">Loading posts...</div>';
        
        const posts = await apiCall('/api/posts?limit=20');
        currentPosts = posts;
        displayPosts(posts);
    } catch (error) {
        postsContainer.innerHTML = 
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
    if (!confirm(`Delete "${title}"?\n\nThis cannot be undone.`)) return;
    
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

async function uploadFromUrl() {
    const url = document.getElementById('media-url').value.trim();
    const title = document.getElementById('media-title').value.trim();
    
    if (!url) {
        showNotification('Please enter a media URL', 'error');
        return;
    }
    
    try {
        showNotification('Uploading media...', 'info');
        
        const result = await apiCall('/api/media/upload', {
            method: 'POST',
            body: JSON.stringify({
                url: url,
                title: title || null
            })
        });
        
        showNotification(`Media uploaded successfully! ID: ${result.id}`, 'success');
        document.getElementById('media-url').value = '';
        document.getElementById('media-title').value = '';
        
        // Show uploaded media info
        const info = `
            <div class="success">
                <h4>📷 Media Uploaded</h4>
                <p><strong>Title:</strong> ${escapeHtml(result.title)}</p>
                <p><strong>URL:</strong> <a href="${result.url}" target="_blank">View Media</a></p>
            </div>
        `;
        document.getElementById('quick-info').innerHTML = info;
    } catch (error) {
        showNotification(`Error uploading media: ${error.message}`, 'error');
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

// Chat Interface Functions
async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Clear input
    input.value = '';
    
    // Add user message to chat
    addChatMessage(message, 'user');
    
    // Show typing indicator
    const typingId = addChatMessage('Thinking...', 'assistant', true);
    
    try {
        // Send message to API
        const response = await apiCall('/api/chat', {
            method: 'POST',
            body: JSON.stringify({ message: message })
        });
        
        // Remove typing indicator
        document.getElementById(typingId).remove();
        
        // Add assistant response
        addChatResponse(response);
        
    } catch (error) {
        // Remove typing indicator
        document.getElementById(typingId).remove();
        
        // Add error message
        addChatMessage(`Sorry, I encountered an error: ${error.message}`, 'assistant error');
    }
}

function addChatMessage(message, sender, isTyping = false) {
    const container = document.getElementById('chat-container');
    const messageDiv = document.createElement('div');
    const messageId = 'msg-' + Date.now();
    
    messageDiv.id = messageId;
    messageDiv.className = `chat-message ${sender}`;
    
    if (sender === 'user') {
        messageDiv.innerHTML = `<strong>👤 You:</strong> ${escapeHtml(message)}`;
    } else {
        messageDiv.innerHTML = `<strong>🤖 Assistant:</strong> ${escapeHtml(message)}`;
    }
    
    if (isTyping) {
        messageDiv.style.opacity = '0.7';
        messageDiv.style.fontStyle = 'italic';
    }
    
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
    
    return messageId;
}

function addChatResponse(response) {
    const container = document.getElementById('chat-container');
    const messageDiv = document.createElement('div');
    
    let className = 'chat-message assistant';
    if (response.type === 'error') {
        className += ' error';
    }
    
    messageDiv.className = className;
    
    // Build message content
    let content = `<strong>🤖 Assistant:</strong> ${escapeHtml(response.message)}`;
    
    // Add actions if available
    if (response.actions && response.actions.length > 0) {
        content += '<div class="chat-actions">';
        response.actions.forEach(action => {
            if (typeof action === 'string') {
                content += `<button class="chat-action-btn" onclick="executeChatAction('${escapeHtml(action)}')">${escapeHtml(action)}</button>`;
            } else if (typeof action === 'object') {
                const actionJson = JSON.stringify(action).replace(/"/g, '&quot;').replace(/'/g, '&#39;');
                const label = action.label || action.type;
                content += `<button class="chat-action-btn" onclick='executeChatAction(${actionJson})'>${escapeHtml(label)}</button>`;
            }
        });
        content += '</div>';
    }
    
    messageDiv.innerHTML = content;
    container.appendChild(messageDiv);
    
    // Add suggestions if available
    if (response.suggestions && response.suggestions.length > 0) {
        updateChatSuggestions(response.suggestions);
    }
    
    // Handle special response types
    if (response.type === 'help' && response.commands) {
        addHelpCommands(response.commands);
    }
    
    container.scrollTop = container.scrollHeight;
}

function addHelpCommands(commands) {
    const container = document.getElementById('chat-container');
    const helpDiv = document.createElement('div');
    helpDiv.className = 'chat-message assistant';
    
    let content = '<strong>📋 Available Commands:</strong><br><br>';
    
    commands.forEach(category => {
        content += `<strong>${category.category}:</strong><br>`;
        category.commands.forEach(cmd => {
            content += `• <code onclick="document.getElementById('chat-input').value='${cmd}'" style="cursor: pointer; background: #f0f0f0; padding: 2px 4px; border-radius: 3px;">${cmd}</code><br>`;
        });
        content += '<br>';
    });
    
    helpDiv.innerHTML = content;
    container.appendChild(helpDiv);
    container.scrollTop = container.scrollHeight;
}

function updateChatSuggestions(suggestions) {
    const suggestionsContainer = document.getElementById('chat-suggestions');
    suggestionsContainer.innerHTML = '';
    
    suggestions.forEach(suggestion => {
        const btn = document.createElement('button');
        btn.className = 'suggestion-btn';
        btn.textContent = suggestion;
        btn.onclick = () => {
            document.getElementById('chat-input').value = suggestion;
            sendChatMessage();
        };
        suggestionsContainer.appendChild(btn);
    });
}

function executeChatAction(actionData) {
    // Handle different types of actions
    if (typeof actionData === 'string') {
        // Simple text action - put in chat input
        document.getElementById('chat-input').value = actionData;
        sendChatMessage();
    } else if (typeof actionData === 'object') {
        // Complex action object
        handleComplexAction(actionData);
    }
}

async function handleComplexAction(action) {
    try {
        switch (action.type) {
            case 'import_urls':
                await importInstagramUrls(action.urls);
                break;
            case 'create_csv_template':
                downloadCsvTemplate();
                break;
            case 'sample_import':
                await sampleInstagramImport();
                break;
            // Apify Instagram actions
            case 'apify_status':
                await checkApifyStatus();
                break;
            case 'apify_scrape_user':
                await scrapeInstagramUser(action.username, action.limit || 20);
                break;
            case 'apify_bulk_import':
                await bulkImportInstagramUser(action.username, action.limit || 10);
                break;
            case 'apify_scrape_urls':
                await scrapeInstagramUrls(action.urls);
                break;
            case 'apify_profile':
                await getInstagramProfile(action.username);
                break;
            case 'cache_stats':
                await getCacheStats();
                break;
            case 'clear_expired_cache':
                await clearExpiredCache();
                break;
            case 'clear_user_cache':
                await clearUserCache(action.username);
                break;
            case 'clear_all_cache':
                await clearAllCache();
                break;
            // Instagram OAuth actions - COMMENTED OUT (using manual import instead)
            // case 'instagram_login':
            //     window.location.href = action.url || '/auth/instagram';
            //     break;
            // case 'instagram_logout':
            //     if (!action.confirm || confirm('Disconnect Instagram account?')) {
            //         await disconnectInstagram();
            //     }
            //     break;
            // case 'check_instagram_status':
            //     await checkInstagramStatus();
            //     break;
            // case 'import_authenticated_posts':
            //     await importAuthenticatedPosts(action.limit || 10);
            //     break;
            default:
                // Fallback to text action
                document.getElementById('chat-input').value = action.label || action.type;
                sendChatMessage();
        }
    } catch (error) {
        addChatMessage('system', `Error executing action: ${error.message}`);
    }
}

async function importInstagramUrls(urls) {
    try {
        addChatMessage('system', `🔄 Importing ${urls.length} Instagram post(s)...`);
        
        // First, extract post data from URLs
        const response = await apiCall('/api/instagram/import-urls', {
            method: 'POST',
            body: JSON.stringify({ urls: urls })
        });
        
        if (response.success && response.posts.length > 0) {
            addChatMessage('system', `✅ Extracted ${response.posts.length} posts. Importing to WordPress...`);
            
            // Then import to WordPress
            const wpResponse = await apiCall('/api/instagram/import-to-wordpress', {
                method: 'POST',
                body: JSON.stringify({ posts: response.posts })
            });
            
            if (wpResponse.success) {
                addChatMessage('system', `🎉 Successfully imported ${wpResponse.imported_count} posts to WordPress as drafts!`);
                loadPosts(); // Refresh the posts list
            } else {
                addChatMessage('system', `❌ WordPress import failed: ${wpResponse.error}`);
            }
        } else {
            addChatMessage('system', `❌ Could not extract posts from URLs: ${response.error || 'Unknown error'}`);
        }
    } catch (error) {
        addChatMessage('system', `❌ Import failed: ${error.message}`);
    }
}

function downloadCsvTemplate() {
    const csvContent = `caption,image_url,post_url,hashtags
"Sample Instagram post caption with #hashtags #example","https://example.com/image1.jpg","https://www.instagram.com/p/ABC123/","hashtags,example"
"Another sample post for Card My Yard #cardmyyard #signs","https://example.com/image2.jpg","https://www.instagram.com/p/DEF456/","cardmyyard,signs"`;
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'instagram_import_template.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    addChatMessage('system', '📄 CSV template downloaded! Fill it with your Instagram data and use the import feature.');
}

async function sampleInstagramImport() {
    const sampleUrls = [
        'https://www.instagram.com/p/sample1/',
        'https://www.instagram.com/p/sample2/'
    ];
    
    addChatMessage('system', '🧪 This would import sample posts from @cardmyyard_oviedo. Replace with real Instagram URLs to test.');
}

// Apify Instagram Integration Functions
async function checkApifyStatus() {
    try {
        addChatMessage('system', '🔍 Checking Apify integration status...');
        
        const response = await apiCall('/api/instagram/apify/status');
        
        if (response.available) {
            const usage = response.usage_info;
            let message = '✅ Apify integration is ready!';
            if (usage && usage.plan) {
                message += ` Plan: ${usage.plan}`;
            }
            addChatMessage('system', message);
        } else {
            addChatMessage('system', '❌ Apify not configured. Set APIFY_API_TOKEN in environment variables.');
        }
    } catch (error) {
        addChatMessage('system', `❌ Error checking Apify status: ${error.message}`);
    }
}

async function scrapeInstagramUser(username, limit = 20) {
    try {
        addChatMessage('system', `🔄 Scraping @${username} via Apify (limit: ${limit})...`);
        
        const response = await apiCall('/api/instagram/apify/scrape-user', {
            method: 'POST',
            body: JSON.stringify({ 
                username: username,
                limit: limit 
            })
        });
        
        if (response.success) {
            addChatMessage('system', `✅ Scraped ${response.posts_count} posts from @${username}`);
            
            // Show option to import to WordPress
            const importBtn = document.createElement('button');
            importBtn.className = 'chat-action-btn';
            importBtn.textContent = 'Import to WordPress';
            importBtn.onclick = () => importApifyPostsToWordPress(response.posts);
            
            const container = document.getElementById('chat-container');
            const lastMessage = container.lastElementChild;
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'chat-actions';
            actionsDiv.appendChild(importBtn);
            lastMessage.appendChild(actionsDiv);
            
            return response.posts;
        } else {
            addChatMessage('system', `❌ Scraping failed: ${response.error}`);
        }
    } catch (error) {
        addChatMessage('system', `❌ Scraping failed: ${error.message}`);
    }
}

async function bulkImportInstagramUser(username, limit = 10) {
    try {
        addChatMessage('system', `🚀 Bulk importing @${username} via Apify (limit: ${limit})...`);
        
        const response = await apiCall('/api/instagram/apify/bulk-import', {
            method: 'POST',
            body: JSON.stringify({ 
                username: username,
                limit: limit 
            })
        });
        
        if (response.success) {
            addChatMessage('system', `🎉 Successfully imported ${response.imported_count} of ${response.scraped_count} posts from @${username} to WordPress!`);
            loadPosts(); // Refresh the posts list
        } else {
            addChatMessage('system', `❌ Bulk import failed: ${response.error || 'Unknown error'}`);
        }
    } catch (error) {
        addChatMessage('system', `❌ Bulk import failed: ${error.message}`);
    }
}

async function scrapeInstagramUrls(urls) {
    try {
        addChatMessage('system', `🔄 Scraping ${urls.length} Instagram URLs via Apify...`);
        
        const response = await apiCall('/api/instagram/apify/scrape-urls', {
            method: 'POST',
            body: JSON.stringify({ urls: urls })
        });
        
        if (response.success) {
            addChatMessage('system', `✅ Scraped ${response.posts_count} posts from ${response.urls_count} URLs`);
            
            // Show option to import to WordPress
            const importBtn = document.createElement('button');
            importBtn.className = 'chat-action-btn';
            importBtn.textContent = 'Import to WordPress';
            importBtn.onclick = () => importApifyPostsToWordPress(response.posts);
            
            const container = document.getElementById('chat-container');
            const lastMessage = container.lastElementChild;
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'chat-actions';
            actionsDiv.appendChild(importBtn);
            lastMessage.appendChild(actionsDiv);
            
            return response.posts;
        } else {
            addChatMessage('system', `❌ URL scraping failed: ${response.error}`);
        }
    } catch (error) {
        addChatMessage('system', `❌ URL scraping failed: ${error.message}`);
    }
}

async function importApifyPostsToWordPress(posts) {
    try {
        addChatMessage('system', `📥 Importing ${posts.length} Apify posts to WordPress...`);
        
        const response = await apiCall('/api/instagram/apify/import-to-wordpress', {
            method: 'POST',
            body: JSON.stringify({ posts: posts })
        });
        
        if (response.success) {
            addChatMessage('system', `🎉 Successfully imported ${response.imported_count} of ${response.total_posts} posts to WordPress as drafts!`);
            loadPosts(); // Refresh the posts list
        } else {
            addChatMessage('system', `❌ WordPress import failed: ${response.error}`);
        }
    } catch (error) {
        addChatMessage('system', `❌ WordPress import failed: ${error.message}`);
    }
}

async function getInstagramProfile(username) {
    try {
        addChatMessage('system', `👤 Getting profile info for @${username}...`);
        
        const response = await apiCall(`/api/instagram/apify/profile/${username}`);
        
        if (response.success && response.profile) {
            const profile = response.profile;
            let message = `✅ Profile found for @${username}:\n`;
            message += `• Full name: ${profile.full_name || 'N/A'}\n`;
            message += `• Followers: ${profile.followers_count || 'N/A'}\n`;
            message += `• Following: ${profile.following_count || 'N/A'}\n`;
            message += `• Posts: ${profile.posts_count || 'N/A'}\n`;
            message += `• Verified: ${profile.is_verified ? 'Yes' : 'No'}\n`;
            message += `• Private: ${profile.is_private ? 'Yes' : 'No'}`;
            
            addChatMessage('system', message);
        } else {
            addChatMessage('system', `❌ Profile not found for @${username}`);
        }
    } catch (error) {
        addChatMessage('system', `❌ Error getting profile: ${error.message}`);
    }
}

// Cache Management Functions
async function getCacheStats() {
    try {
        addChatMessage('system', '📊 Getting cache statistics...');
        
        const response = await apiCall('/api/instagram/apify/cache/stats');
        
        if (response.success) {
            const stats = response.cache_stats;
            let message = '📊 Cache Statistics:\n';
            message += `• Total files: ${stats.total_files}\n`;
            message += `• Total size: ${(stats.total_size_bytes / 1024).toFixed(1)} KB\n`;
            
            if (stats.oldest_entry) {
                message += `• Oldest entry: ${new Date(stats.oldest_entry).toLocaleString()}\n`;
            }
            if (stats.newest_entry) {
                message += `• Newest entry: ${new Date(stats.newest_entry).toLocaleString()}\n`;
            }
            
            if (stats.by_operation && Object.keys(stats.by_operation).length > 0) {
                message += '\n📁 By operation:\n';
                for (const [operation, opStats] of Object.entries(stats.by_operation)) {
                    message += `• ${operation}: ${opStats.files} files (${(opStats.size_bytes / 1024).toFixed(1)} KB)`;
                    if (opStats.expired > 0) {
                        message += ` - ${opStats.expired} expired`;
                    }
                    message += '\n';
                }
            }
            
            addChatMessage('system', message);
        } else {
            addChatMessage('system', `❌ Error getting cache stats: ${response.error}`);
        }
    } catch (error) {
        addChatMessage('system', `❌ Error getting cache stats: ${error.message}`);
    }
}

async function clearExpiredCache() {
    try {
        addChatMessage('system', '🧹 Clearing expired cache entries...');
        
        const response = await apiCall('/api/instagram/apify/cache/clear-expired', {
            method: 'POST'
        });
        
        if (response.success) {
            addChatMessage('system', `✅ ${response.message}`);
        } else {
            addChatMessage('system', `❌ Error clearing cache: ${response.error}`);
        }
    } catch (error) {
        addChatMessage('system', `❌ Error clearing cache: ${error.message}`);
    }
}

async function clearUserCache(username) {
    try {
        addChatMessage('system', `🧹 Clearing cache for @${username}...`);
        
        const response = await apiCall(`/api/instagram/apify/cache/clear-user/${username}`, {
            method: 'POST'
        });
        
        if (response.success) {
            addChatMessage('system', `✅ ${response.message}`);
        } else {
            addChatMessage('system', `❌ Error clearing user cache: ${response.error}`);
        }
    } catch (error) {
        addChatMessage('system', `❌ Error clearing user cache: ${error.message}`);
    }
}

async function clearAllCache() {
    if (!confirm('Clear ALL cached Apify data? This cannot be undone.')) {
        return;
    }
    
    try {
        addChatMessage('system', '🧹 Clearing all cache entries...');
        
        const response = await apiCall('/api/instagram/apify/cache/clear-all', {
            method: 'POST'
        });
        
        if (response.success) {
            addChatMessage('system', `✅ ${response.message}`);
        } else {
            addChatMessage('system', `❌ Error clearing all cache: ${response.error}`);
        }
    } catch (error) {
        addChatMessage('system', `❌ Error clearing all cache: ${error.message}`);
    }
}

// Instagram OAuth functions - COMMENTED OUT (using manual import instead)
// async function checkInstagramStatus() {
//     try {
//         addChatMessage('system', '🔍 Checking Instagram connection...');
//         
//         const response = await apiCall('/api/instagram/status');
//         
//         if (response.authenticated) {
//             addChatMessage('system', `✅ Connected to Instagram as @${response.username}`);
//         } else {
//             addChatMessage('system', '❌ Not connected to Instagram. Use "connect instagram" to authenticate.');
//         }
//     } catch (error) {
//         addChatMessage('system', `❌ Error checking Instagram status: ${error.message}`);
//     }
// }

// async function disconnectInstagram() {
//     try {
//         addChatMessage('system', '🔌 Disconnecting Instagram...');
//         
//         const response = await apiCall('/api/instagram/disconnect', {
//             method: 'POST'
//         });
//         
//         if (response.success) {
//             addChatMessage('system', '✅ Instagram account disconnected successfully');
//         } else {
//             addChatMessage('system', `❌ Failed to disconnect: ${response.error}`);
//         }
//     } catch (error) {
//         addChatMessage('system', `❌ Error disconnecting Instagram: ${error.message}`);
//     }
// }

// async function importAuthenticatedPosts(limit = 10) {
//     try {
//         addChatMessage('system', `📥 Importing your latest ${limit} Instagram posts...`);
//         
//         const response = await apiCall('/api/instagram/import-authenticated', {
//             method: 'POST',
//             body: JSON.stringify({ limit: limit })
//         });
//         
//         if (response.success) {
//             addChatMessage('system', `🎉 Successfully imported ${response.imported_count} of ${response.total_available} posts to WordPress as drafts!`);
//             loadPosts(); // Refresh the posts list
//         } else {
//             addChatMessage('system', `❌ Import failed: ${response.error}`);
//         }
//     } catch (error) {
//         if (error.message.includes('401')) {
//             addChatMessage('system', '🔐 Instagram authentication required. Use "connect instagram" first.');
//         } else {
//             addChatMessage('system', `❌ Import failed: ${error.message}`);
//         }
//     }
// }

// Instagram Post Viewer Functions
let currentPostIndex = 0;

function displayInstagramPosts(posts) {
    currentPosts = posts;
    currentPostIndex = 0;
    
    if (posts.length === 0) {
        showEmptyPostViewer();
        return;
    }
    
    showPostViewer();
    displayCurrentPost();
}

function showEmptyPostViewer() {
    const postDisplay = document.getElementById('post-display');
    postDisplay.innerHTML = `
        <div class="empty-state">
            <div class="icon">📱</div>
            <h3>No Instagram Posts Found</h3>
            <p>Try scraping a different username or check if the account exists</p>
        </div>
    `;
}

function showPostViewer() {
    const postDisplay = document.getElementById('post-display');
    postDisplay.innerHTML = `
        <img id="post-image" class="post-image" src="" alt="Instagram post" />
        <div class="post-content">
            <div class="post-meta">
                <span id="post-username"></span>
                <span id="post-date"></span>
            </div>
            <div id="post-caption" class="post-caption"></div>
            <div id="post-hashtags" class="post-hashtags"></div>
            <div style="font-size: 0.9em; color: #666;">
                <span id="post-engagement"></span>
            </div>
        </div>
        <div class="post-actions">
            <button class="btn success" onclick="importCurrentPostToWordPress()">
                📝 Import to WordPress
            </button>
            <button class="btn secondary" onclick="viewPostOnInstagram()">
                🔗 View on Instagram
            </button>
        </div>
        <div class="post-navigation">
            <button class="nav-btn" id="prev-btn" onclick="previousPost()" disabled>
                ← Previous
            </button>
            <span class="post-counter" id="post-counter">1 of 1</span>
            <button class="nav-btn" id="next-btn" onclick="nextPost()" disabled>
                Next →
            </button>
        </div>
    `;
}

function displayCurrentPost() {
    if (currentPosts.length === 0) return;
    
    const post = currentPosts[currentPostIndex];
    
    // Update image
    const postImage = document.getElementById('post-image');
    if (postImage) {
        postImage.src = post.image_url || '';
        postImage.alt = post.alt_text || 'Instagram post';
    }
    
    // Update content
    const usernameEl = document.getElementById('post-username');
    if (usernameEl) usernameEl.textContent = `@${post.username}`;
    
    const dateEl = document.getElementById('post-date');
    if (dateEl) dateEl.textContent = post.date_posted || '';
    
    const captionEl = document.getElementById('post-caption');
    if (captionEl) captionEl.textContent = post.caption || '';
    
    const hashtagsEl = document.getElementById('post-hashtags');
    if (hashtagsEl) {
        const hashtags = post.hashtags || [];
        hashtagsEl.textContent = hashtags.map(tag => `#${tag}`).join(' ');
    }
    
    const engagementEl = document.getElementById('post-engagement');
    if (engagementEl) {
        engagementEl.textContent = `❤️ ${post.likes_count || 0} likes • 💬 ${post.comments_count || 0} comments`;
    }
    
    // Update navigation
    const counterEl = document.getElementById('post-counter');
    if (counterEl) {
        counterEl.textContent = `${currentPostIndex + 1} of ${currentPosts.length}`;
    }
    
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    
    if (prevBtn) prevBtn.disabled = currentPostIndex === 0;
    if (nextBtn) nextBtn.disabled = currentPostIndex === currentPosts.length - 1;
}

function previousPost() {
    if (currentPostIndex > 0) {
        currentPostIndex--;
        displayCurrentPost();
    }
}

function nextPost() {
    if (currentPostIndex < currentPosts.length - 1) {
        currentPostIndex++;
        displayCurrentPost();
    }
}

function importCurrentPostToWordPress() {
    if (currentPosts.length === 0) return;
    
    const post = currentPosts[currentPostIndex];
    
    // Show loading state
    const importBtn = document.querySelector('.post-actions .btn.success');
    const originalText = importBtn.textContent;
    importBtn.textContent = '⏳ Importing...';
    importBtn.disabled = true;
    
    // Import the single post
    importApifyPostsToWordPress([post]).then(() => {
        // Reset button
        importBtn.textContent = '✅ Imported!';
        setTimeout(() => {
            importBtn.textContent = originalText;
            importBtn.disabled = false;
        }, 2000);
    }).catch(() => {
        // Reset button on error
        importBtn.textContent = originalText;
        importBtn.disabled = false;
    });
}

function viewPostOnInstagram() {
    if (currentPosts.length === 0) return;
    
    const post = currentPosts[currentPostIndex];
    if (post.post_url) {
        window.open(post.post_url, '_blank');
    }
}

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    if (currentPosts.length === 0) return;
    
    if (e.key === 'ArrowLeft') {
        e.preventDefault();
        previousPost();
    } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        nextPost();
    } else if (e.key === 'Enter' && e.ctrlKey) {
        e.preventDefault();
        importCurrentPostToWordPress();
    }
});

// Update existing scraping functions to use the new viewer
async function scrapeInstagramUser(username, limit = 20) {
    try {
        addChatMessage('system', `🔄 Scraping @${username} via Apify (limit: ${limit})...`);
        
        const response = await apiCall('/api/instagram/apify/scrape-user', {
            method: 'POST',
            body: JSON.stringify({ 
                username: username,
                limit: limit 
            })
        });
        
        if (response.success) {
            addChatMessage('system', `✅ Scraped ${response.posts_count} posts from @${username}`);
            
            // Display posts in the viewer
            displayInstagramPosts(response.posts);
            
            return response.posts;
        } else {
            addChatMessage('system', `❌ Scraping failed: ${response.error}`);
            showEmptyPostViewer();
        }
    } catch (error) {
        addChatMessage('system', `❌ Scraping failed: ${error.message}`);
        showEmptyPostViewer();
    }
}

async function scrapeInstagramUrls(urls) {
    try {
        addChatMessage('system', `🔄 Scraping ${urls.length} Instagram URLs via Apify...`);
        
        const response = await apiCall('/api/instagram/apify/scrape-urls', {
            method: 'POST',
            body: JSON.stringify({ urls: urls })
        });
        
        if (response.success) {
            addChatMessage('system', `✅ Scraped ${response.posts_count} posts from ${response.urls_count} URLs`);
            
            // Display posts in the viewer
            displayInstagramPosts(response.posts);
            
            return response.posts;
        } else {
            addChatMessage('system', `❌ URL scraping failed: ${response.error}`);
            showEmptyPostViewer();
        }
    } catch (error) {
        addChatMessage('system', `❌ URL scraping failed: ${error.message}`);
        showEmptyPostViewer();
    }
}