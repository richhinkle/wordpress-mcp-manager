"""
AI Chat Handler for WordPress MCP Manager
Processes natural language commands and converts them to WordPress actions
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class WordPressChatHandler:
    """Handles natural language chat commands for WordPress management"""
    
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        self.conversation_history = []
        
    def process_message(self, message: str, user_context: Dict = None) -> Dict[str, Any]:
        """Process a chat message and return response with actions"""
        
        # Clean and normalize the message
        message = message.strip().lower()
        
        # Store in conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_message': message,
            'context': user_context or {}
        })
        
        try:
            # Parse the message and determine intent
            intent, params = self._parse_intent(message)
            
            # Execute the appropriate action
            result = self._execute_action(intent, params)
            
            # Store response in history
            self.conversation_history[-1]['response'] = result
            
            return result
            
        except Exception as e:
            error_response = {
                'type': 'error',
                'message': f"Sorry, I encountered an error: {str(e)}",
                'suggestions': [
                    "Try rephrasing your request",
                    "Ask 'what can you do?' to see available commands",
                    "Check if your WordPress site is accessible"
                ]
            }
            self.conversation_history[-1]['response'] = error_response
            return error_response
    
    def _parse_intent(self, message: str) -> tuple:
        """Parse user message to determine intent and extract parameters"""
        
        # Help and information commands
        if any(phrase in message for phrase in ['help', 'what can you do', 'commands', 'how to']):
            return 'help', {}
        
        if any(phrase in message for phrase in ['site health', 'check site', 'status', 'ping']):
            return 'site_health', {}
        
        # Post management commands
        if message.startswith('create post') or message.startswith('write post') or message.startswith('new post'):
            title = self._extract_quoted_text(message) or self._extract_after_keyword(message, ['create post', 'write post', 'new post'])
            return 'create_post', {'title': title}
        
        if message.startswith('list posts') or message.startswith('show posts') or 'my posts' in message:
            return 'list_posts', {}
        
        if message.startswith('list drafts') or message.startswith('show drafts'):
            return 'list_drafts', {}
        
        if message.startswith('publish post'):
            post_id = self._extract_number(message)
            return 'publish_post', {'post_id': post_id}
        
        if message.startswith('delete post'):
            post_id = self._extract_number(message)
            return 'delete_post', {'post_id': post_id}
        
        # Search commands
        if message.startswith('search') or message.startswith('find'):
            query = self._extract_quoted_text(message) or self._extract_after_keyword(message, ['search', 'find'])
            return 'search_posts', {'query': query}
        
        # Media commands
        if 'generate image' in message or 'create image' in message or 'ai image' in message:
            prompt = self._extract_quoted_text(message) or self._extract_after_keyword(message, ['generate image', 'create image', 'ai image'])
            return 'generate_image', {'prompt': prompt}
        
        if 'upload image' in message or 'upload media' in message:
            url = self._extract_url(message)
            return 'upload_media', {'url': url}
        
        # Site information commands
        if 'list plugins' in message or 'show plugins' in message:
            return 'list_plugins', {}
        
        if 'list users' in message or 'show users' in message:
            return 'list_users', {}
        
        if 'create user' in message:
            return 'create_user_help', {}
        
        if 'count posts' in message or 'post count' in message:
            post_type = self._extract_after_keyword(message, ['count posts', 'post count']) or 'post'
            return 'count_posts', {'post_type': post_type}
        
        # Media management commands
        if 'list media' in message or 'show media' in message:
            return 'list_media', {}
        
        if 'count media' in message or 'media count' in message:
            return 'count_media', {}
        
        # Taxonomy commands
        if 'list categories' in message or 'show categories' in message:
            return 'list_categories', {}
        
        if 'list tags' in message or 'show tags' in message:
            return 'list_tags', {}
        
        if 'create category' in message:
            name = self._extract_quoted_text(message) or self._extract_after_keyword(message, ['create category'])
            return 'create_category', {'name': name}
        
        if 'create tag' in message:
            name = self._extract_quoted_text(message) or self._extract_after_keyword(message, ['create tag'])
            return 'create_tag', {'name': name}
        
        # Comment commands
        if 'list comments' in message or 'show comments' in message:
            return 'list_comments', {}
        
        if 'moderate comments' in message or 'pending comments' in message:
            return 'moderate_comments', {}
        
        # Site options commands
        if 'site title' in message and ('get' in message or 'show' in message):
            return 'get_site_title', {}
        
        if 'site description' in message and ('get' in message or 'show' in message):
            return 'get_site_description', {}
        
        # Post meta commands
        if 'post meta' in message or 'custom fields' in message:
            post_id = self._extract_number(message)
            return 'get_post_meta', {'post_id': post_id}
        
        # Content creation with AI assistance
        if message.startswith('write about') or message.startswith('create content about'):
            topic = self._extract_after_keyword(message, ['write about', 'create content about'])
            return 'ai_content', {'topic': topic}
        
        # Instagram authentication commands - COMMENTED OUT (using manual import instead)
        # if 'connect instagram' in message or 'login instagram' in message or 'instagram login' in message:
        #     return 'instagram_connect', {}
        # 
        # if 'disconnect instagram' in message or 'instagram logout' in message:
        #     return 'instagram_disconnect', {}
        # 
        # if 'instagram status' in message or 'instagram account' in message:
        #     return 'instagram_status', {}
        
        # Instagram import commands (handle typos and variations)
        if ('import instagram' in message or 'instagram import' in message or 
            'import instragram' in message or 'instragram import' in message):
            # Check for URLs in the message
            urls = self._extract_urls(message)
            if urls:
                return 'import_instagram_urls', {'urls': urls}
            else:
                return 'import_instagram_help', {}
            # OAuth-based import commented out (using manual import instead)
            # if 'my posts' in message or 'my instagram' in message or 'authenticated' in message:
            #     # Import from authenticated account
            #     limit = self._extract_number(message) or 10
            #     return 'import_instagram_authenticated', {'limit': limit}
        
        if 'instagram help' in message or 'instagram commands' in message:
            return 'instagram_help', {}
        
        # Apify Instagram commands
        if 'apify status' in message or 'check apify' in message:
            return 'apify_status', {}
        
        if 'scrape instagram' in message or 'apify scrape' in message:
            # Extract username from message
            username = self._extract_instagram_username(message)
            limit = self._extract_number(message) or 20
            
            if 'bulk import' in message or 'import to wordpress' in message:
                return 'apify_bulk_import', {'username': username, 'limit': limit}
            else:
                return 'apify_scrape_user', {'username': username, 'limit': limit}
        
        if 'instagram profile' in message and ('get' in message or 'show' in message or 'check' in message):
            username = self._extract_instagram_username(message)
            return 'apify_profile', {'username': username}
        
        if 'apify help' in message or 'apify commands' in message:
            return 'apify_help', {}
        
        # Cache management commands
        if 'cache stats' in message or 'cache statistics' in message:
            return 'cache_stats', {}
        
        if 'clear cache' in message:
            if 'expired' in message:
                return 'clear_expired_cache', {}
            elif 'all' in message:
                return 'clear_all_cache', {}
            else:
                # Check for username
                username = self._extract_instagram_username(message)
                if username:
                    return 'clear_user_cache', {'username': username}
                else:
                    return 'clear_cache_help', {}
        
        # Default: treat as general question or request for clarification
        return 'general', {'message': message}
    
    def _execute_action(self, intent: str, params: Dict) -> Dict[str, Any]:
        """Execute the determined action and return formatted response"""
        
        if intent == 'help':
            return self._help_response()
        
        elif intent == 'site_health':
            return self._site_health_response()
        
        elif intent == 'create_post':
            return self._create_post_response(params)
        
        elif intent == 'list_posts':
            return self._list_posts_response()
        
        elif intent == 'list_drafts':
            return self._list_drafts_response()
        
        elif intent == 'publish_post':
            return self._publish_post_response(params)
        
        elif intent == 'delete_post':
            return self._delete_post_response(params)
        
        elif intent == 'search_posts':
            return self._search_posts_response(params)
        
        elif intent == 'generate_image':
            return self._generate_image_response(params)
        
        elif intent == 'upload_media':
            return self._upload_media_response(params)
        
        elif intent == 'list_plugins':
            return self._list_plugins_response()
        
        elif intent == 'list_users':
            return self._list_users_response()
        
        elif intent == 'ai_content':
            return self._ai_content_response(params)
        
        elif intent == 'import_instagram_urls':
            return self._import_instagram_urls_response(params)
        
        elif intent == 'import_instagram_help':
            return self._import_instagram_help_response()
        
        elif intent == 'instagram_help':
            return self._instagram_help_response()
        
        # Apify Instagram actions
        elif intent == 'apify_status':
            return self._apify_status_response()
        
        elif intent == 'apify_scrape_user':
            return self._apify_scrape_user_response(params)
        
        elif intent == 'apify_bulk_import':
            return self._apify_bulk_import_response(params)
        
        elif intent == 'apify_profile':
            return self._apify_profile_response(params)
        
        elif intent == 'apify_help':
            return self._apify_help_response()
        
        # Cache management actions
        elif intent == 'cache_stats':
            return self._cache_stats_response()
        
        elif intent == 'clear_expired_cache':
            return self._clear_expired_cache_response()
        
        elif intent == 'clear_user_cache':
            return self._clear_user_cache_response(params)
        
        elif intent == 'clear_all_cache':
            return self._clear_all_cache_response()
        
        elif intent == 'clear_cache_help':
            return self._clear_cache_help_response()
        
        # Instagram OAuth actions - COMMENTED OUT (using manual import instead)
        # elif intent == 'instagram_connect':
        #     return self._instagram_connect_response()
        # 
        # elif intent == 'instagram_disconnect':
        #     return self._instagram_disconnect_response()
        # 
        # elif intent == 'instagram_status':
        #     return self._instagram_status_response()
        # 
        # elif intent == 'import_instagram_authenticated':
        #     return self._import_instagram_authenticated_response(params)
        
        elif intent == 'create_user_help':
            return self._create_user_help_response()
        
        elif intent == 'count_posts':
            return self._count_posts_response(params)
        
        elif intent == 'list_media':
            return self._list_media_response()
        
        elif intent == 'count_media':
            return self._count_media_response()
        
        elif intent == 'list_categories':
            return self._list_categories_response()
        
        elif intent == 'list_tags':
            return self._list_tags_response()
        
        elif intent == 'create_category':
            return self._create_category_response(params)
        
        elif intent == 'create_tag':
            return self._create_tag_response(params)
        
        elif intent == 'list_comments':
            return self._list_comments_response()
        
        elif intent == 'moderate_comments':
            return self._moderate_comments_response()
        
        elif intent == 'get_site_title':
            return self._get_site_title_response()
        
        elif intent == 'get_site_description':
            return self._get_site_description_response()
        
        elif intent == 'get_post_meta':
            return self._get_post_meta_response(params)
        
        else:
            return self._general_response(params)
    
    def _help_response(self) -> Dict[str, Any]:
        """Return help information"""
        return {
            'type': 'help',
            'message': "I can help you manage your WordPress site! Here's what I can do:",
            'commands': [
                {
                    'category': 'Post Management',
                    'commands': [
                        "create post 'My New Post'",
                        "list posts",
                        "list drafts", 
                        "publish post 123",
                        "delete post 123",
                        "search 'keyword'"
                    ]
                },
                {
                    'category': 'Content Creation',
                    'commands': [
                        "write about 'topic'",
                        "generate image 'description'",
                        "upload image https://example.com/image.jpg"
                    ]
                },
                {
                    'category': 'Site Information',
                    'commands': [
                        "site health",
                        "list plugins",
                        "list users",
                        "count posts",
                        "site title",
                        "site description"
                    ]
                },
                {
                    'category': 'Media Management',
                    'commands': [
                        "list media",
                        "count media",
                        "upload image [URL]",
                        "generate image 'description'"
                    ]
                },
                {
                    'category': 'Categories & Tags',
                    'commands': [
                        "list categories",
                        "list tags", 
                        "create category 'name'",
                        "create tag 'name'"
                    ]
                },
                {
                    'category': 'Comments',
                    'commands': [
                        "list comments",
                        "moderate comments",
                        "pending comments"
                    ]
                },
                {
                    'category': 'Advanced',
                    'commands': [
                        "post meta 123",
                        "custom fields 123",
                        "create user",
                        "count media"
                    ]
                },
                {
                    'category': 'Instagram Integration',
                    'commands': [
                        "import instagram post [URL]",
                        "import instagram posts [URL1] [URL2]",
                        "instagram help"
                    ]
                },
                {
                    'category': 'Apify Instagram (Professional)',
                    'commands': [
                        "apify status",
                        "scrape instagram @username",
                        "bulk import @username",
                        "instagram profile @username",
                        "apify help"
                    ]
                },
                {
                    'category': 'Cache Management',
                    'commands': [
                        "cache stats",
                        "clear expired cache",
                        "clear cache @username",
                        "clear all cache"
                    ]
                }
            ]
        }
    
    def _site_health_response(self) -> Dict[str, Any]:
        """Check and return site health"""
        try:
            result = self.mcp_client.ping()
            return {
                'type': 'success',
                'message': f"✅ Your WordPress site '{result.get('name')}' is online and responding!",
                'data': result
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Site health check failed: {str(e)}",
                'suggestions': ["Check your WordPress URL and access token"]
            }
    
    def _create_post_response(self, params: Dict) -> Dict[str, Any]:
        """Create a new post"""
        title = params.get('title')
        if not title:
            return {
                'type': 'question',
                'message': "What would you like the post title to be?",
                'next_action': 'create_post_with_title'
            }
        
        try:
            # Create a draft post with basic content
            content = f"This post was created via chat interface.\n\nTitle: {title}\n\nAdd your content here..."
            
            result = self.mcp_client.create_post(
                title=title,
                content=content,
                status='draft'
            )
            
            return {
                'type': 'success',
                'message': f"✅ Created draft post '{title}' with ID {result.get('ID')}",
                'data': result,
                'actions': [
                    f"publish post {result.get('ID')}",
                    "list drafts",
                    f"edit post {result.get('ID')}"
                ]
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to create post: {str(e)}"
            }
    
    def _list_posts_response(self) -> Dict[str, Any]:
        """List recent posts"""
        try:
            posts = self.mcp_client.get_posts(limit=10)
            
            # Ensure posts is a list
            if not isinstance(posts, list):
                return {
                    'type': 'error',
                    'message': f"❌ Unexpected response format from WordPress: {type(posts)}",
                    'suggestions': ["Check WordPress connection", "Try 'site health'"]
                }
            
            if not posts:
                return {
                    'type': 'info',
                    'message': "📄 No posts found. Would you like to create your first post?",
                    'suggestions': ["create post 'My First Post'"]
                }
            
            post_list = []
            # Safely iterate through posts
            for i, post in enumerate(posts):
                if i >= 5:  # Only show first 5
                    break
                if isinstance(post, dict):
                    status_emoji = "📝" if post.get('post_status') == 'draft' else "✅"
                    title = post.get('post_title', 'Untitled')
                    post_id = post.get('ID', 'Unknown')
                    post_list.append(f"{status_emoji} {title} (ID: {post_id})")
            
            if not post_list:
                return {
                    'type': 'info',
                    'message': "📄 No valid posts found in response.",
                    'suggestions': ["Check WordPress connection", "Try 'site health'"]
                }
            
            message = f"📚 Found {len(posts)} posts. Here are the most recent:\n\n" + "\n".join(post_list)
            
            if len(posts) > 5:
                message += f"\n\n... and {len(posts) - 5} more posts"
            
            return {
                'type': 'success',
                'message': message,
                'data': posts,
                'actions': ["list drafts", "search posts", "create post"]
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to load posts: {str(e)}"
            }
    
    def _list_drafts_response(self) -> Dict[str, Any]:
        """List draft posts"""
        try:
            drafts = self.mcp_client.get_posts(post_status='draft', limit=10)
            
            # Ensure drafts is a list
            if not isinstance(drafts, list):
                return {
                    'type': 'error',
                    'message': f"❌ Unexpected response format from WordPress: {type(drafts)}",
                    'suggestions': ["Check WordPress connection", "Try 'site health'"]
                }
            
            if not drafts:
                return {
                    'type': 'info',
                    'message': "📝 No draft posts found. All your posts are published!",
                    'suggestions': ["create post 'New Draft'", "list posts"]
                }
            
            draft_list = []
            valid_drafts = []
            for draft in drafts:
                if isinstance(draft, dict):
                    title = draft.get('post_title', 'Untitled')
                    post_id = draft.get('ID', 'Unknown')
                    draft_list.append(f"📝 {title} (ID: {post_id})")
                    valid_drafts.append(draft)
            
            if not draft_list:
                return {
                    'type': 'info',
                    'message': "📝 No valid draft posts found.",
                    'suggestions': ["create post 'New Draft'", "list posts"]
                }
            
            message = f"📝 Found {len(valid_drafts)} draft posts:\n\n" + "\n".join(draft_list)
            
            return {
                'type': 'success',
                'message': message,
                'data': valid_drafts,
                'actions': [f"publish post {draft.get('ID')}" for draft in valid_drafts[:3] if draft.get('ID')]
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to load drafts: {str(e)}"
            }
    
    def _publish_post_response(self, params: Dict) -> Dict[str, Any]:
        """Publish a post"""
        post_id = params.get('post_id')
        if not post_id:
            return {
                'type': 'question',
                'message': "Which post would you like to publish? Please provide the post ID.",
                'suggestions': ["list drafts"]
            }
        
        try:
            result = self.mcp_client.update_post(post_id, {'post_status': 'publish'})
            return {
                'type': 'success',
                'message': f"✅ Published post ID {post_id} successfully!",
                'data': result,
                'actions': ["list posts", f"view post {post_id}"]
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to publish post: {str(e)}",
                'suggestions': ["list drafts", "check post ID"]
            }
    
    def _search_posts_response(self, params: Dict) -> Dict[str, Any]:
        """Search posts"""
        query = params.get('query')
        if not query:
            return {
                'type': 'question',
                'message': "What would you like to search for?",
                'suggestions': ["search 'keyword'", "list posts"]
            }
        
        try:
            posts = self.mcp_client.get_posts(search=query, limit=10)
            
            if not posts:
                return {
                    'type': 'info',
                    'message': f"🔍 No posts found matching '{query}'",
                    'suggestions': ["try different keywords", "list all posts"]
                }
            
            post_list = []
            for post in posts[:5]:
                status_emoji = "📝" if post.get('post_status') == 'draft' else "✅"
                post_list.append(f"{status_emoji} {post.get('post_title')} (ID: {post.get('ID')})")
            
            message = f"🔍 Found {len(posts)} posts matching '{query}':\n\n" + "\n".join(post_list)
            
            return {
                'type': 'success',
                'message': message,
                'data': posts
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Search failed: {str(e)}"
            }
    
    def _generate_image_response(self, params: Dict) -> Dict[str, Any]:
        """Generate AI image"""
        prompt = params.get('prompt')
        if not prompt:
            return {
                'type': 'question',
                'message': "What kind of image would you like me to generate?",
                'suggestions': ["generate image 'sunset over mountains'"]
            }
        
        try:
            result = self.mcp_client.generate_ai_image(prompt)
            return {
                'type': 'success',
                'message': f"🎨 Generated AI image: '{prompt}'",
                'data': result,
                'image_url': result.get('url'),
                'actions': ["create post with this image"]
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to generate image: {str(e)}"
            }
    
    def _ai_content_response(self, params: Dict) -> Dict[str, Any]:
        """Generate AI content for a topic"""
        topic = params.get('topic')
        if not topic:
            return {
                'type': 'question',
                'message': "What topic would you like me to write about?",
                'suggestions': ["write about 'artificial intelligence'"]
            }
        
        # Generate content outline/structure
        content_outline = f"""# {topic.title()}

## Introduction
Brief introduction to {topic}...

## Main Points
- Key point 1 about {topic}
- Key point 2 about {topic}
- Key point 3 about {topic}

## Conclusion
Summary and final thoughts on {topic}...

---
*This content outline was generated by AI. Please expand and customize as needed.*"""
        
        try:
            result = self.mcp_client.create_post(
                title=f"About {topic.title()}",
                content=content_outline,
                status='draft'
            )
            
            return {
                'type': 'success',
                'message': f"✅ Created content outline for '{topic}' as draft post (ID: {result.get('ID')})",
                'data': result,
                'actions': [
                    f"publish post {result.get('ID')}",
                    f"edit post {result.get('ID')}",
                    "list drafts"
                ]
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to create content: {str(e)}"
            }
    
    def _list_plugins_response(self) -> Dict[str, Any]:
        """List WordPress plugins"""
        try:
            plugins = self.mcp_client.list_plugins()
            
            plugin_list = []
            for plugin in plugins[:10]:  # Show top 10
                plugin_list.append(f"🔌 {plugin.get('Name')} (v{plugin.get('Version')})")
            
            message = f"🔌 Found {len(plugins)} plugins:\n\n" + "\n".join(plugin_list)
            
            if len(plugins) > 10:
                message += f"\n\n... and {len(plugins) - 10} more plugins"
            
            return {
                'type': 'success',
                'message': message,
                'data': plugins
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to load plugins: {str(e)}"
            }
    
    def _list_users_response(self) -> Dict[str, Any]:
        """List WordPress users"""
        try:
            users = self.mcp_client.get_users(limit=10)
            
            user_list = []
            for user in users:
                roles = ', '.join(user.get('roles', [])) if user.get('roles') else 'No role'
                user_list.append(f"👤 {user.get('display_name')} ({roles})")
            
            message = f"👥 Found {len(users)} users:\n\n" + "\n".join(user_list)
            
            return {
                'type': 'success',
                'message': message,
                'data': users
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to load users: {str(e)}"
            }
    
    def _general_response(self, params: Dict) -> Dict[str, Any]:
        """Handle general messages"""
        message = params.get('message', '')
        
        # Try to provide helpful suggestions based on keywords
        suggestions = []
        
        if any(word in message for word in ['post', 'article', 'blog']):
            suggestions.extend(["create post 'title'", "list posts", "list drafts"])
        
        if any(word in message for word in ['image', 'picture', 'photo']):
            suggestions.extend(["generate image 'description'", "upload image URL"])
        
        if any(word in message for word in ['site', 'website', 'wordpress']):
            suggestions.extend(["site health", "list plugins", "list users"])
        
        if not suggestions:
            suggestions = ["help", "list posts", "site health"]
        
        return {
            'type': 'clarification',
            'message': "I'm not sure I understand. Could you try rephrasing that?",
            'suggestions': suggestions[:3]  # Limit to 3 suggestions
        }
    
    def _import_instagram_urls_response(self, params: Dict) -> Dict[str, Any]:
        """Handle Instagram URL import"""
        urls = params.get('urls', [])
        
        if not urls:
            return {
                'type': 'error',
                'message': "No Instagram URLs found in your message.",
                'suggestions': [
                    "Try: 'import instagram post https://www.instagram.com/p/ABC123/'",
                    "You can import multiple URLs at once",
                    "Ask 'instagram help' for more options"
                ]
            }
        
        return {
            'type': 'instagram_import',
            'message': f"I found {len(urls)} Instagram URL(s) to import:",
            'urls': urls,
            'actions': [
                {
                    'type': 'import_urls',
                    'label': f'Import {len(urls)} Instagram Post(s)',
                    'urls': urls
                }
            ],
            'suggestions': [
                "Click the import button to process these URLs",
                "The posts will be imported as WordPress drafts",
                "Images will be uploaded to your media library"
            ]
        }
    
    def _import_instagram_help_response(self) -> Dict[str, Any]:
        """Provide Instagram import help"""
        return {
            'type': 'help',
            'message': "I can help you import Instagram posts to WordPress! Here are your options:",
            'commands': [
                "📱 **Import from URLs**: 'import instagram post [URL]'",
                "📋 **Multiple URLs**: 'import instagram posts [URL1] [URL2]'", 
                "📄 **CSV Import**: Upload a CSV file with post data",
                "✋ **Manual Entry**: Add posts manually through the interface"
            ],
            'actions': [
                {
                    'type': 'create_csv_template',
                    'label': 'Download CSV Template',
                    'description': 'Get a template for bulk Instagram import'
                }
            ],
            'suggestions': [
                "Start with a single Instagram post URL",
                "Use CSV import for bulk operations",
                "All imports create WordPress drafts first"
            ]
        }
    
    def _instagram_help_response(self) -> Dict[str, Any]:
        """Provide comprehensive Instagram help"""
        return {
            'type': 'help',
            'message': "Instagram Integration Commands:",
            'commands': [
                "🔗 **Import Single Post**: 'import instagram post https://instagram.com/p/ABC123/'",
                "🔗 **Import Multiple**: 'import instagram posts [URL1] [URL2] [URL3]'",
                "📋 **CSV Import**: 'import instagram csv' (upload CSV file)",
                "❓ **Get Help**: 'instagram help' or 'instagram commands'"
            ],
            'features': [
                "✅ Imports images to WordPress media library",
                "✅ Preserves captions and hashtags", 
                "✅ Creates posts as drafts for review",
                "✅ Adds Instagram metadata to posts",
                "✅ Supports bulk import operations"
            ],
            'actions': [
                {
                    'type': 'sample_import',
                    'label': 'Try Sample Import',
                    'description': 'Test with cardmyyard_oviedo sample data'
                }
            ]
        }
    
    # Instagram OAuth functions - COMMENTED OUT (using manual import instead)
    # def _instagram_connect_response(self) -> Dict[str, Any]:
    #     """Handle Instagram connection request"""
    #     return {
    #         'type': 'instagram_auth',
    #         'message': "Connect your Instagram account to import posts directly from the API!",
    #         'benefits': [
    #             "✅ Legal and reliable access to your Instagram posts",
    #             "✅ No risk of being blocked or rate limited", 
    #             "✅ Access to full resolution images",
    #             "✅ Real-time post data with captions and hashtags"
    #         ],
    #         'actions': [
    #             {
    #                 'type': 'instagram_login',
    #                 'label': '🔗 Connect Instagram Account',
    #                 'url': '/auth/instagram'
    #             }
    #         ],
    #         'suggestions': [
    #             "Click the button above to connect @cardmyyard_oviedo",
    #             "You'll be redirected to Instagram to grant permissions",
    #             "After connecting, you can import posts with 'import my instagram posts'"
    #         ]
    #     }
    
    # def _instagram_disconnect_response(self) -> Dict[str, Any]:
    #     """Handle Instagram disconnection request"""
    #     return {
    #         'type': 'instagram_disconnect',
    #         'message': "Disconnect your Instagram account?",
    #         'actions': [
    #             {
    #                 'type': 'instagram_logout',
    #                 'label': '🔌 Disconnect Instagram',
    #                 'confirm': True
    #             }
    #         ],
    #         'suggestions': [
    #             "This will remove stored access tokens",
    #             "You can reconnect anytime",
    #             "Your WordPress posts will not be affected"
    #         ]
    #     }
    
    # def _instagram_status_response(self) -> Dict[str, Any]:
    #     """Check Instagram connection status"""
    #     return {
    #         'type': 'instagram_status_check',
    #         'message': "Checking Instagram connection status...",
    #         'actions': [
    #             {
    #                 'type': 'check_instagram_status',
    #                 'label': '🔍 Check Status'
    #             }
    #         ]
    #     }
    
    # def _import_instagram_authenticated_response(self, params: Dict) -> Dict[str, Any]:
    #     """Handle authenticated Instagram import"""
    #     limit = params.get('limit', 10)
    #     
    #     return {
    #         'type': 'instagram_authenticated_import',
    #         'message': f"Import your latest {limit} Instagram posts to WordPress?",
    #         'features': [
    #             f"📱 Import {limit} most recent posts",
    #             "🖼️ High-quality images uploaded to media library",
    #             "📝 Captions preserved with hashtags",
    #             "📋 Posts created as drafts for review"
    #         ],
    #         'actions': [
    #             {
    #                 'type': 'import_authenticated_posts',
    #                 'label': f'📥 Import {limit} Posts',
    #                 'limit': limit
    #             },
    #             {
    #                 'type': 'check_instagram_status',
    #                 'label': '🔍 Check Connection First'
    #             }
    #         ],
    #         'suggestions': [
    #             "Make sure you're connected to Instagram first",
    #             "All imports create draft posts for review",
    #             "You can change the number of posts to import"
    #         ]
    #     }
    
    # Utility methods for parsing
    def _extract_quoted_text(self, message: str) -> Optional[str]:
        """Extract text within quotes"""
        matches = re.findall(r"['\"]([^'\"]*)['\"]", message)
        return matches[0] if matches else None
    
    def _extract_after_keyword(self, message: str, keywords: List[str]) -> Optional[str]:
        """Extract text after specific keywords"""
        for keyword in keywords:
            if keyword in message:
                parts = message.split(keyword, 1)
                if len(parts) > 1:
                    return parts[1].strip().strip('"\'')
        return None
    
    def _extract_number(self, message: str) -> Optional[int]:
        """Extract first number from message"""
        numbers = re.findall(r'\d+', message)
        return int(numbers[0]) if numbers else None
    
    def _extract_url(self, message: str) -> Optional[str]:
        """Extract URL from message"""
        urls = re.findall(r'https?://[^\s]+', message)
        return urls[0] if urls else None
    
    def _extract_urls(self, message: str) -> List[str]:
        """Extract all URLs from message"""
        urls = re.findall(r'https?://[^\s]+', message)
        # Filter for Instagram URLs
        instagram_urls = [url for url in urls if 'instagram.com' in url]
        return instagram_urls if instagram_urls else urls
    
    def _extract_instagram_username(self, message: str) -> Optional[str]:
        """Extract Instagram username from message"""
        # Look for @username pattern
        username_match = re.search(r'@([a-zA-Z0-9._]+)', message)
        if username_match:
            return username_match.group(1)
        
        # Look for common username patterns
        patterns = [
            r'user\s+([a-zA-Z0-9._]+)',
            r'username\s+([a-zA-Z0-9._]+)',
            r'account\s+([a-zA-Z0-9._]+)',
            r'scrape\s+([a-zA-Z0-9._]+)',
            r'profile\s+([a-zA-Z0-9._]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    # New response methods for additional WordPress functions
    def _create_user_help_response(self) -> Dict[str, Any]:
        """Provide user creation help"""
        return {
            'type': 'help',
            'message': "To create a WordPress user, I need some information:",
            'required_fields': [
                "👤 Username (required)",
                "📧 Email address (required)",
                "🔒 Password (optional - will generate if not provided)",
                "📝 Display name (optional)",
                "🎭 Role (optional: subscriber, contributor, author, editor, administrator)"
            ],
            'suggestions': [
                "Use the web interface for user creation",
                "Provide: username, email, and role",
                "Passwords will be auto-generated if not specified"
            ]
        }
    
    def _count_posts_response(self, params: Dict) -> Dict[str, Any]:
        """Count posts by type and status"""
        try:
            post_type = params.get('post_type', 'post')
            result = self.mcp_client.count_posts(post_type=post_type)
            
            if isinstance(result, dict):
                total = sum(int(count) for count in result.values() if str(count).isdigit())
                
                status_list = []
                for status, count in result.items():
                    if str(count).isdigit() and int(count) > 0:
                        emoji = "✅" if status == 'publish' else "📝" if status == 'draft' else "📊"
                        status_list.append(f"{emoji} {status.title()}: {count}")
                
                message = f"📊 Post counts for '{post_type}':\n\n" + "\n".join(status_list)
                message += f"\n\n📈 Total: {total} posts"
                
                return {
                    'type': 'success',
                    'message': message,
                    'data': result
                }
            else:
                return {
                    'type': 'info',
                    'message': f"📊 Post count result: {result}",
                    'data': result
                }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to count posts: {str(e)}"
            }
    
    def _list_media_response(self) -> Dict[str, Any]:
        """List media items"""
        try:
            media = self.mcp_client.get_media(limit=10)
            
            if not media:
                return {
                    'type': 'info',
                    'message': "📁 No media files found in your library.",
                    'suggestions': ["upload image URL", "generate ai image"]
                }
            
            media_list = []
            for item in media[:5]:
                if isinstance(item, dict):
                    title = item.get('title', 'Untitled')
                    media_id = item.get('ID', 'Unknown')
                    media_type = item.get('mime_type', 'unknown')
                    media_list.append(f"🖼️ {title} (ID: {media_id}, Type: {media_type})")
            
            message = f"📁 Found {len(media)} media files. Recent uploads:\n\n" + "\n".join(media_list)
            
            return {
                'type': 'success',
                'message': message,
                'data': media,
                'actions': ["upload new media", "count media"]
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to load media: {str(e)}"
            }
    
    def _count_media_response(self) -> Dict[str, Any]:
        """Count media attachments"""
        try:
            result = self.mcp_client.count_media()
            
            return {
                'type': 'success',
                'message': f"📊 Total media files: {result}",
                'data': result,
                'actions': ["list media", "upload media"]
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to count media: {str(e)}"
            }
    
    def _list_categories_response(self) -> Dict[str, Any]:
        """List categories"""
        try:
            categories = self.mcp_client.get_terms('category', limit=20)
            
            if not categories:
                return {
                    'type': 'info',
                    'message': "📂 No categories found.",
                    'suggestions': ["create category 'New Category'"]
                }
            
            cat_list = []
            for cat in categories[:10]:
                if isinstance(cat, dict):
                    name = cat.get('name', 'Unnamed')
                    count = cat.get('count', 0)
                    cat_list.append(f"📂 {name} ({count} posts)")
            
            message = f"📂 Found {len(categories)} categories:\n\n" + "\n".join(cat_list)
            
            return {
                'type': 'success',
                'message': message,
                'data': categories,
                'actions': ["create category", "list tags"]
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to load categories: {str(e)}"
            }
    
    def _list_tags_response(self) -> Dict[str, Any]:
        """List tags"""
        try:
            tags = self.mcp_client.get_terms('post_tag', limit=20)
            
            if not tags:
                return {
                    'type': 'info',
                    'message': "🏷️ No tags found.",
                    'suggestions': ["create tag 'New Tag'"]
                }
            
            tag_list = []
            for tag in tags[:10]:
                if isinstance(tag, dict):
                    name = tag.get('name', 'Unnamed')
                    count = tag.get('count', 0)
                    tag_list.append(f"🏷️ {name} ({count} posts)")
            
            message = f"🏷️ Found {len(tags)} tags:\n\n" + "\n".join(tag_list)
            
            return {
                'type': 'success',
                'message': message,
                'data': tags,
                'actions': ["create tag", "list categories"]
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to load tags: {str(e)}"
            }
    
    def _create_category_response(self, params: Dict) -> Dict[str, Any]:
        """Create a new category"""
        name = params.get('name')
        if not name:
            return {
                'type': 'question',
                'message': "What would you like to name the new category?",
                'suggestions': ["create category 'Technology'"]
            }
        
        try:
            result = self.mcp_client.create_term('category', name)
            return {
                'type': 'success',
                'message': f"✅ Created category '{name}' with ID {result.get('term_id')}",
                'data': result,
                'actions': ["list categories", "create post"]
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to create category: {str(e)}"
            }
    
    def _create_tag_response(self, params: Dict) -> Dict[str, Any]:
        """Create a new tag"""
        name = params.get('name')
        if not name:
            return {
                'type': 'question',
                'message': "What would you like to name the new tag?",
                'suggestions': ["create tag 'WordPress'"]
            }
        
        try:
            result = self.mcp_client.create_term('post_tag', name)
            return {
                'type': 'success',
                'message': f"✅ Created tag '{name}' with ID {result.get('term_id')}",
                'data': result,
                'actions': ["list tags", "create post"]
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to create tag: {str(e)}"
            }
    
    def _list_comments_response(self) -> Dict[str, Any]:
        """List recent comments"""
        try:
            comments = self.mcp_client.get_comments(limit=10)
            
            if not comments:
                return {
                    'type': 'info',
                    'message': "💬 No comments found.",
                    'suggestions': ["Check comment settings", "Encourage user engagement"]
                }
            
            comment_list = []
            for comment in comments[:5]:
                if isinstance(comment, dict):
                    author = comment.get('comment_author', 'Anonymous')
                    content = comment.get('comment_content', '')[:50] + "..."
                    status = comment.get('comment_approved', '1')
                    status_emoji = "✅" if status == '1' else "⏳" if status == '0' else "❌"
                    comment_list.append(f"{status_emoji} {author}: {content}")
            
            message = f"💬 Found {len(comments)} comments. Recent:\n\n" + "\n".join(comment_list)
            
            return {
                'type': 'success',
                'message': message,
                'data': comments,
                'actions': ["moderate comments"]
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to load comments: {str(e)}"
            }
    
    def _moderate_comments_response(self) -> Dict[str, Any]:
        """Show pending comments for moderation"""
        try:
            pending = self.mcp_client.get_comments(status='hold', limit=10)
            
            if not pending:
                return {
                    'type': 'success',
                    'message': "✅ No pending comments to moderate. All caught up!",
                    'actions': ["list all comments"]
                }
            
            pending_list = []
            for comment in pending[:5]:
                if isinstance(comment, dict):
                    author = comment.get('comment_author', 'Anonymous')
                    content = comment.get('comment_content', '')[:50] + "..."
                    comment_id = comment.get('comment_ID')
                    pending_list.append(f"⏳ {author}: {content} (ID: {comment_id})")
            
            message = f"⏳ Found {len(pending)} pending comments:\n\n" + "\n".join(pending_list)
            message += "\n\nUse the WordPress admin to approve or reject these comments."
            
            return {
                'type': 'info',
                'message': message,
                'data': pending,
                'actions': ["list all comments"]
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to load pending comments: {str(e)}"
            }
    
    def _get_site_title_response(self) -> Dict[str, Any]:
        """Get site title"""
        try:
            result = self.mcp_client.get_option('blogname')
            return {
                'type': 'success',
                'message': f"🏠 Site title: {result}",
                'data': result
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to get site title: {str(e)}"
            }
    
    def _get_site_description_response(self) -> Dict[str, Any]:
        """Get site description"""
        try:
            result = self.mcp_client.get_option('blogdescription')
            return {
                'type': 'success',
                'message': f"📝 Site description: {result}",
                'data': result
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to get site description: {str(e)}"
            }
    
    def _get_post_meta_response(self, params: Dict) -> Dict[str, Any]:
        """Get post meta/custom fields"""
        post_id = params.get('post_id')
        if not post_id:
            return {
                'type': 'question',
                'message': "Which post would you like to see custom fields for? Please provide the post ID.",
                'suggestions': ["list posts", "post meta 123"]
            }
        
        try:
            result = self.mcp_client.get_post_meta(post_id)
            
            if not result:
                return {
                    'type': 'info',
                    'message': f"📋 No custom fields found for post ID {post_id}",
                    'suggestions': ["Add custom fields through WordPress admin"]
                }
            
            if isinstance(result, dict):
                meta_list = []
                for key, value in result.items():
                    if isinstance(value, list) and len(value) == 1:
                        value = value[0]
                    meta_list.append(f"🔑 {key}: {str(value)[:50]}...")
                
                message = f"📋 Custom fields for post ID {post_id}:\n\n" + "\n".join(meta_list[:10])
                
                return {
                    'type': 'success',
                    'message': message,
                    'data': result
                }
            else:
                return {
                    'type': 'info',
                    'message': f"📋 Post meta for ID {post_id}: {result}",
                    'data': result
                }
        except Exception as e:
            return {
                'type': 'error',
                'message': f"❌ Failed to get post meta: {str(e)}"
            }
    
    # Apify Instagram Integration Response Methods
    def _apify_status_response(self) -> Dict[str, Any]:
        """Check Apify integration status"""
        return {
            'type': 'apify_status_check',
            'message': "Checking Apify Instagram scraper status...",
            'actions': [
                {
                    'type': 'apify_status',
                    'label': '🔍 Check Apify Status'
                }
            ],
            'suggestions': [
                "Apify provides professional Instagram scraping",
                "Get your API token from console.apify.com",
                "More reliable than manual scraping methods"
            ]
        }
    
    def _apify_scrape_user_response(self, params: Dict) -> Dict[str, Any]:
        """Scrape Instagram user posts via Apify"""
        username = params.get('username')
        limit = params.get('limit', 20)
        
        if not username:
            return {
                'type': 'question',
                'message': "Which Instagram username would you like to scrape?",
                'suggestions': [
                    "scrape instagram @cardmyyard_oviedo",
                    "scrape instagram user cardmyyard_oviedo",
                    "Try with any public Instagram account"
                ]
            }
        
        return {
            'type': 'apify_scrape',
            'message': f"Scrape @{username} via Apify (limit: {limit} posts)?",
            'features': [
                f"🔍 Professional scraping of @{username}",
                f"📱 Up to {limit} recent posts",
                "🖼️ High-quality images and engagement data",
                "📊 Likes, comments, and hashtag extraction",
                "⚡ Fast and reliable scraping"
            ],
            'actions': [
                {
                    'type': 'apify_scrape_user',
                    'label': f'🔍 Scrape @{username}',
                    'username': username,
                    'limit': limit
                }
            ],
            'suggestions': [
                "Scraped posts can be imported to WordPress",
                "All data includes engagement metrics",
                "Works with any public Instagram account"
            ]
        }
    
    def _apify_bulk_import_response(self, params: Dict) -> Dict[str, Any]:
        """Bulk import Instagram user posts via Apify"""
        username = params.get('username')
        limit = params.get('limit', 10)
        
        if not username:
            return {
                'type': 'question',
                'message': "Which Instagram username would you like to bulk import?",
                'suggestions': [
                    "bulk import @cardmyyard_oviedo",
                    "scrape and import cardmyyard_oviedo",
                    "Try with any public Instagram account"
                ]
            }
        
        return {
            'type': 'apify_bulk_import',
            'message': f"Bulk import @{username} to WordPress via Apify?",
            'process': [
                f"1️⃣ Scrape {limit} recent posts from @{username}",
                "2️⃣ Download high-quality images",
                "3️⃣ Create WordPress draft posts",
                "4️⃣ Add engagement metrics and metadata",
                "5️⃣ Set featured images automatically"
            ],
            'actions': [
                {
                    'type': 'apify_bulk_import',
                    'label': f'🚀 Bulk Import @{username}',
                    'username': username,
                    'limit': limit
                }
            ],
            'suggestions': [
                "All posts will be created as drafts",
                "Images uploaded to WordPress media library",
                "Includes likes, comments, and hashtags"
            ]
        }
    
    def _apify_profile_response(self, params: Dict) -> Dict[str, Any]:
        """Get Instagram profile info via Apify"""
        username = params.get('username')
        
        if not username:
            return {
                'type': 'question',
                'message': "Which Instagram profile would you like to check?",
                'suggestions': [
                    "instagram profile @cardmyyard_oviedo",
                    "get profile cardmyyard_oviedo",
                    "check instagram account cardmyyard_oviedo"
                ]
            }
        
        return {
            'type': 'apify_profile',
            'message': f"Get profile information for @{username}?",
            'info': [
                "👤 Full name and bio",
                "📊 Follower and following counts",
                "📱 Total posts count",
                "✅ Verification status",
                "🔒 Privacy status"
            ],
            'actions': [
                {
                    'type': 'apify_profile',
                    'label': f'👤 Get @{username} Profile',
                    'username': username
                }
            ],
            'suggestions': [
                "Profile data helps plan content strategy",
                "Check account status before scraping",
                "Works with any public Instagram account"
            ]
        }
    
    def _apify_help_response(self) -> Dict[str, Any]:
        """Provide Apify integration help"""
        return {
            'type': 'help',
            'message': "Apify Instagram Integration Commands:",
            'commands': [
                "🔍 **Check Status**: 'apify status' or 'check apify'",
                "📱 **Scrape User**: 'scrape instagram @username' or 'apify scrape username'",
                "🚀 **Bulk Import**: 'bulk import @username' or 'scrape and import username'",
                "👤 **Get Profile**: 'instagram profile @username' or 'get profile username'",
                "❓ **Get Help**: 'apify help' or 'apify commands'"
            ],
            'features': [
                "✅ Professional Instagram scraping service",
                "✅ High-quality images and engagement data",
                "✅ Bulk operations with rate limiting",
                "✅ Direct WordPress integration",
                "✅ Reliable and maintained by Apify"
            ],
            'setup': [
                "1️⃣ Get API token from console.apify.com",
                "2️⃣ Set APIFY_API_TOKEN environment variable",
                "3️⃣ Restart the application",
                "4️⃣ Use 'apify status' to verify setup"
            ],
            'actions': [
                {
                    'type': 'apify_status',
                    'label': '🔍 Check Apify Status'
                }
            ],
            'suggestions': [
                "Apify is more reliable than manual scraping",
                "Includes engagement metrics and metadata",
                "Professional service with proper rate limiting"
            ]
        }
    
    # Cache Management Response Methods
    def _cache_stats_response(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'type': 'cache_stats',
            'message': "Getting Apify cache statistics...",
            'actions': [
                {
                    'type': 'cache_stats',
                    'label': '📊 Get Cache Stats'
                }
            ],
            'suggestions': [
                "Cache helps reduce API costs",
                "Results are stored locally for faster access",
                "Use 'clear expired cache' to clean up old data"
            ]
        }
    
    def _clear_expired_cache_response(self) -> Dict[str, Any]:
        """Clear expired cache entries"""
        return {
            'type': 'clear_expired_cache',
            'message': "Clear expired cache entries to free up space?",
            'actions': [
                {
                    'type': 'clear_expired_cache',
                    'label': '🧹 Clear Expired Cache'
                }
            ],
            'suggestions': [
                "This removes only expired entries",
                "Fresh cache entries will be preserved",
                "Helps keep cache size manageable"
            ]
        }
    
    def _clear_user_cache_response(self, params: Dict) -> Dict[str, Any]:
        """Clear cache for specific user"""
        username = params.get('username')
        
        if not username:
            return {
                'type': 'question',
                'message': "Which user's cache would you like to clear?",
                'suggestions': [
                    "clear cache @cardmyyard_oviedo",
                    "clear cache for username",
                    "Use 'cache stats' to see what's cached"
                ]
            }
        
        return {
            'type': 'clear_user_cache',
            'message': f"Clear all cached data for @{username}?",
            'info': [
                f"🗑️ Remove cached posts for @{username}",
                f"🗑️ Remove cached profile for @{username}",
                "💡 Next request will fetch fresh data from Apify"
            ],
            'actions': [
                {
                    'type': 'clear_user_cache',
                    'label': f'🧹 Clear @{username} Cache',
                    'username': username
                }
            ],
            'suggestions': [
                "Use this if you need fresh data for a user",
                "Cached data will be refetched on next request",
                "Helps when user has new posts or profile changes"
            ]
        }
    
    def _clear_all_cache_response(self) -> Dict[str, Any]:
        """Clear all cache entries"""
        return {
            'type': 'clear_all_cache',
            'message': "⚠️ Clear ALL cached Apify data?",
            'warning': [
                "🚨 This will remove ALL cached Instagram data",
                "💰 Next requests will use Apify API credits",
                "⏱️ Requests will be slower until cache rebuilds",
                "❌ This action cannot be undone"
            ],
            'actions': [
                {
                    'type': 'clear_all_cache',
                    'label': '🗑️ Clear All Cache',
                    'confirm': True
                }
            ],
            'suggestions': [
                "Consider 'clear expired cache' first",
                "Only use if you need completely fresh data",
                "This will increase your Apify API usage"
            ]
        }
    
    def _clear_cache_help_response(self) -> Dict[str, Any]:
        """Provide cache management help"""
        return {
            'type': 'help',
            'message': "Cache Management Commands:",
            'commands': [
                "📊 **Cache Stats**: 'cache stats' or 'cache statistics'",
                "🧹 **Clear Expired**: 'clear expired cache'",
                "👤 **Clear User**: 'clear cache @username'",
                "🗑️ **Clear All**: 'clear all cache' (use with caution)"
            ],
            'benefits': [
                "💰 Reduces Apify API costs by reusing data",
                "⚡ Faster response times for cached data",
                "📊 Automatic expiration keeps data fresh",
                "🎯 Selective clearing for specific users"
            ],
            'actions': [
                {
                    'type': 'cache_stats',
                    'label': '📊 View Cache Stats'
                },
                {
                    'type': 'clear_expired_cache',
                    'label': '🧹 Clear Expired'
                }
            ],
            'suggestions': [
                "Check cache stats to see what's stored",
                "Clear expired cache regularly to save space",
                "Only clear all cache if you need completely fresh data"
            ]
        }