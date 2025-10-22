"""
Instagram OAuth Integration for WordPress MCP Manager
Handles Instagram Basic Display API authentication and data access
"""

import requests
import json
import os
from urllib.parse import urlencode
from typing import Dict, List, Optional
import time
from datetime import datetime

class InstagramOAuth:
    """Handle Instagram OAuth flow and API access"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
        # Instagram Business API endpoints (via Facebook)
        self.auth_url = "https://www.facebook.com/v18.0/dialog/oauth"
        self.token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
        self.graph_url = "https://graph.facebook.com"
        
        self.session = requests.Session()
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate Instagram authorization URL for user to visit
        """
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'instagram_basic,pages_read_engagement',
            'response_type': 'code'
        }
        
        if state:
            params['state'] = state
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        
        # Debug logging
        print(f"=== Instagram OAuth URL Debug ===")
        print(f"Auth URL: {self.auth_url}")
        print(f"Client ID: {self.client_id}")
        print(f"Redirect URI: {self.redirect_uri}")
        print(f"Scope: instagram_basic,pages_read_engagement")
        print(f"Full URL: {auth_url}")
        print(f"================================")
        
        return auth_url
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange authorization code for access token
        """
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri,
                'code': code
            }
            
            response = self.session.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Get long-lived token
            if 'access_token' in token_data:
                long_lived_token = self.get_long_lived_token(token_data['access_token'])
                if long_lived_token:
                    token_data.update(long_lived_token)
            
            return token_data
            
        except Exception as e:
            print(f"Error exchanging code for token: {e}")
            return {}
    
    def get_long_lived_token(self, short_token: str) -> Dict:
        """
        Exchange short-lived token for long-lived token (60 days)
        """
        try:
            params = {
                'grant_type': 'ig_exchange_token',
                'client_secret': self.client_secret,
                'access_token': short_token
            }
            
            response = self.session.get(f"{self.graph_url}/access_token", params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error getting long-lived token: {e}")
            return {}
    
    def refresh_token(self, access_token: str) -> Dict:
        """
        Refresh long-lived token (extends for another 60 days)
        """
        try:
            params = {
                'grant_type': 'ig_refresh_token',
                'access_token': access_token
            }
            
            response = self.session.get(f"{self.graph_url}/refresh_access_token", params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return {}
    
    def get_user_profile(self, access_token: str) -> Dict:
        """
        Get user's Instagram profile information
        """
        try:
            params = {
                'fields': 'id,username,account_type,media_count',
                'access_token': access_token
            }
            
            response = self.session.get(f"{self.graph_url}/me", params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return {}
    
    def get_user_media(self, access_token: str, limit: int = 25) -> List[Dict]:
        """
        Get user's Instagram media (posts)
        """
        try:
            params = {
                'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp',
                'limit': limit,
                'access_token': access_token
            }
            
            response = self.session.get(f"{self.graph_url}/me/media", params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', [])
            
        except Exception as e:
            print(f"Error getting user media: {e}")
            return []
    
    def get_media_details(self, media_id: str, access_token: str) -> Dict:
        """
        Get detailed information about a specific media item
        """
        try:
            params = {
                'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,children',
                'access_token': access_token
            }
            
            response = self.session.get(f"{self.graph_url}/{media_id}", params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error getting media details: {e}")
            return {}
    
    def format_instagram_post(self, media_data: Dict, username: str = None) -> Dict:
        """
        Format Instagram API response into our standard post format
        """
        try:
            # Extract hashtags from caption
            caption = media_data.get('caption', '')
            hashtags = []
            if caption:
                import re
                hashtags = re.findall(r'#(\w+)', caption)
            
            # Get the best image URL
            image_url = media_data.get('media_url', '')
            if media_data.get('media_type') == 'VIDEO':
                image_url = media_data.get('thumbnail_url', image_url)
            
            # Parse timestamp
            timestamp_str = media_data.get('timestamp', '')
            timestamp = 0
            date_posted = ''
            
            if timestamp_str:
                try:
                    # Instagram timestamp format: 2023-01-01T12:00:00+0000
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    timestamp = int(dt.timestamp())
                    date_posted = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    timestamp = int(time.time())
                    date_posted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            formatted_post = {
                'id': media_data.get('id', ''),
                'shortcode': media_data.get('id', ''),  # API doesn't provide shortcode directly
                'username': username or 'instagram_user',
                'caption': caption,
                'image_url': image_url,
                'post_url': media_data.get('permalink', ''),
                'timestamp': timestamp,
                'date_posted': date_posted,
                'hashtags': hashtags,
                'media_type': media_data.get('media_type', 'IMAGE'),
                'is_video': media_data.get('media_type') == 'VIDEO',
                'extraction_method': 'instagram_api'
            }
            
            return formatted_post
            
        except Exception as e:
            print(f"Error formatting Instagram post: {e}")
            return {}

class InstagramTokenManager:
    """Manage Instagram access tokens for users"""
    
    def __init__(self, storage_file: str = 'instagram_tokens.json'):
        self.storage_file = storage_file
        self.tokens = self.load_tokens()
    
    def load_tokens(self) -> Dict:
        """Load tokens from storage file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading tokens: {e}")
        return {}
    
    def save_tokens(self):
        """Save tokens to storage file"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.tokens, f, indent=2)
        except Exception as e:
            print(f"Error saving tokens: {e}")
    
    def store_token(self, user_id: str, token_data: Dict):
        """Store token data for a user"""
        self.tokens[user_id] = {
            'access_token': token_data.get('access_token'),
            'expires_in': token_data.get('expires_in'),
            'created_at': int(time.time()),
            'user_id': token_data.get('user_id'),
            'username': token_data.get('username', '')
        }
        self.save_tokens()
    
    def get_token(self, user_id: str) -> Optional[str]:
        """Get valid access token for user"""
        if user_id in self.tokens:
            token_info = self.tokens[user_id]
            
            # Check if token is still valid (with some buffer)
            created_at = token_info.get('created_at', 0)
            expires_in = token_info.get('expires_in', 3600)
            
            if time.time() - created_at < (expires_in - 86400):  # 1 day buffer
                return token_info.get('access_token')
        
        return None
    
    def remove_token(self, user_id: str):
        """Remove token for user"""
        if user_id in self.tokens:
            del self.tokens[user_id]
            self.save_tokens()

def test_instagram_oauth():
    """Test Instagram OAuth setup (requires environment variables)"""
    
    client_id = os.getenv('INSTAGRAM_CLIENT_ID')
    client_secret = os.getenv('INSTAGRAM_CLIENT_SECRET')
    redirect_uri = os.getenv('INSTAGRAM_REDIRECT_URI', 'http://localhost:5000/auth/instagram/callback')
    
    if not client_id or not client_secret:
        print("❌ Instagram OAuth credentials not found in environment variables")
        print("Set INSTAGRAM_CLIENT_ID and INSTAGRAM_CLIENT_SECRET")
        return
    
    oauth = InstagramOAuth(client_id, client_secret, redirect_uri)
    
    print("=" * 60)
    print("Instagram OAuth Test")
    print("=" * 60)
    
    # Generate authorization URL
    auth_url = oauth.get_authorization_url(state='test_state')
    print(f"\n🔗 Authorization URL:")
    print(f"{auth_url}")
    
    print(f"\n📋 Setup Instructions:")
    print(f"1. Visit the URL above")
    print(f"2. Login with Instagram account (@cardmyyard_oviedo)")
    print(f"3. Grant permissions to your app")
    print(f"4. Copy the 'code' parameter from the callback URL")
    print(f"5. Use the code to get access token")
    
    print(f"\n⚙️  Environment Variables Needed:")
    print(f"INSTAGRAM_CLIENT_ID={client_id}")
    print(f"INSTAGRAM_CLIENT_SECRET=[hidden]")
    print(f"INSTAGRAM_REDIRECT_URI={redirect_uri}")

if __name__ == "__main__":
    test_instagram_oauth()