# AIWU WordPress MCP Integration Setup Guide

This guide shows how to connect Kiro IDE to WordPress using the AIWU plugin's MCP (Model Context Protocol) functionality.

## Prerequisites

1. **WordPress site** with admin access
2. **Kiro IDE** installed
3. **Python** installed on your system
4. **uv package manager** installed (`pip install uv`)

## Step 1: WordPress Setup

1. **Install AIWU Plugin**
   - Go to WordPress Admin → Plugins → Add New
   - Search for "AI Copilot - Content Generator" (this is the AIWU plugin)
   - Install and activate the plugin

2. **Configure AIWU MCP Settings**
   - Go to AIWU plugin settings
   - Find "AI MCP Integration" section
   - Enable MCP: ✅ On
   - Enable MCP Logging: ✅ On (optional, for debugging)
   - Generate an Access Token (32-character string)
   - Note your MCP URL: `https://your-site.com/wp-json/mcp/v1/sse`

3. **Server Requirements**
   - HTTPS certificate (required)
   - Public IP access
   - Disable caching for `/wp-json/mcp/v1/sse` endpoint
   - Configure security (Mod_Security, Cloudflare) to allow MCP requests

## Step 2: Create MCP Bridge Server

Create a file called `wordpress_mcp_server.py` in your project directory:

```python
#!/usr/bin/env python3
"""
Proper MCP Server for WordPress AIWU plugin
"""
import sys
import json
import requests
from typing import Any, Dict

# Update these with your WordPress details
WORDPRESS_URL = "https://your-site.com/wp-json/mcp/v1/sse"
ACCESS_TOKEN = "your-32-character-access-token"

class WordPressMCPServer:
    def __init__(self):
        self.tools = []
        
    def handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request"""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": "wordpress-aiwu",
                    "version": "1.0.0"
                }
            }
        }
    
    def handle_tools_list(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request - forward to WordPress"""
        try:
            # Forward tools/list request to WordPress
            url = f"{WORDPRESS_URL}?token={ACCESS_TOKEN}"
            wp_request = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "method": "tools/list"
            }
            
            response = requests.post(url, json=wp_request, headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Kiro-MCP-Client/1.0"
            }, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                # Fallback to basic tools if WordPress doesn't respond
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "tools": [
                            {
                                "name": "wordpress_posts",
                                "description": "List WordPress posts",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {},
                                    "required": []
                                }
                            }
                        ]
                    }
                }
                
        except Exception as e:
            # Fallback on error
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "tools": [
                        {
                            "name": "wordpress_connection_test",
                            "description": f"WordPress connection failed: {str(e)}",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        }
                    ]
                }
            }
    
    def handle_tools_call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request - forward to WordPress"""
        try:
            # Forward the entire tools/call request to WordPress
            url = f"{WORDPRESS_URL}?token={ACCESS_TOKEN}"
            
            response = requests.post(url, json=request, headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Kiro-MCP-Client/1.0"
            }, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32000,
                        "message": f"WordPress error: {response.status_code} - {response.text[:200]}"
                    }
                }
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32000,
                    "message": f"Connection error: {str(e)}"
                }
            }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route MCP requests to appropriate handlers"""
        method = request.get("method")
        
        if method == "initialize":
            return self.handle_initialize(request)
        elif method == "tools/list":
            return self.handle_tools_list(request)
        elif method == "tools/call":
            return self.handle_tools_call(request)
        else:
            # Forward any other methods to WordPress
            try:
                url = f"{WORDPRESS_URL}?token={ACCESS_TOKEN}"
                response = requests.post(url, json=request, headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "Kiro-MCP-Client/1.0"
                }, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32000,
                        "message": f"Connection error: {str(e)}"
                    }
                }
    
    def run(self):
        """Main stdio loop"""
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    request = json.loads(line)
                    response = self.handle_request(request)
                    print(json.dumps(response), flush=True)
                except json.JSONDecodeError:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                    
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Server error: {e}", file=sys.stderr)

if __name__ == "__main__":
    server = WordPressMCPServer()
    server.run()
```

## Step 3: Configure Kiro MCP

1. **Create MCP Configuration**
   - Create/edit `.kiro/settings/mcp.json` in your workspace:

```json
{
  "mcpServers": {
    "aiwu-wordpress": {
      "command": "python",
      "args": [
        "wordpress_mcp_server.py"
      ],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

2. **Update Bridge Server Configuration**
   - Edit `wordpress_mcp_server.py`
   - Replace `WORDPRESS_URL` with your site's MCP endpoint
   - Replace `ACCESS_TOKEN` with your generated token

## Step 4: Test Connection

1. **Check MCP Server Status**
   - Open Kiro IDE
   - Go to MCP Server view in the feature panel
   - Look for `aiwu-wordpress` server with green checkmark

2. **Test Basic Functionality**
   ```
   mcp_ping                 # Test connection
   wp_list_plugins          # List WordPress plugins
   wp_get_posts             # Get WordPress posts
   ```

## Available WordPress Functions (36 total)

### System Functions
- `mcp_ping` - Test connection
- `wp_list_plugins` - List installed plugins

### Content Management
- `wp_get_post_types`, `wp_get_posts`, `wp_get_post`
- `wp_create_post`, `wp_update_post`, `wp_delete_post`
- `wp_count_posts`

### Post Meta & Custom Fields
- `wp_get_post_meta`, `wp_update_post_meta`, `wp_delete_post_meta`

### Taxonomies (Categories & Tags)
- `wp_get_taxonomies`, `wp_get_terms`, `wp_create_term`
- `wp_update_term`, `wp_delete_term`
- `wp_get_post_terms`, `wp_add_post_terms`, `wp_count_terms`

### Media Management
- `wp_get_media`, `wp_upload_media`, `wp_update_media`
- `wp_delete_media`, `wp_set_featured_image`, `wp_count_media`
- `aiwu_image` - Generate AI images

### User Management
- `wp_get_users`, `wp_create_user`, `wp_update_user`

### Comments
- `wp_get_comments`, `wp_create_comment`, `wp_update_comment`, `wp_delete_comment`

### Site Options
- `wp_get_option`, `wp_update_option`

## Troubleshooting

### Common Issues

1. **"uvx not recognized" error**
   - Install uv: `pip install uv`
   - Restart terminal/Kiro after installation

2. **"Connection timeout" error**
   - Check WordPress site accessibility
   - Verify AIWU plugin is active
   - Check access token is correct

3. **"406 Not Acceptable" error**
   - Configure Mod_Security to allow MCP endpoint
   - Disable Cloudflare protection for MCP endpoint
   - Ensure caching is disabled for `/wp-json/mcp/v1/sse`

4. **"Red X" in MCP Server view**
   - Check MCP logs for specific error messages
   - Verify Python script path is correct
   - Ensure `requests` library is installed: `pip install requests`

### Security Considerations

- Keep access tokens secure and rotate regularly
- Use HTTPS for all connections
- Configure proper WordPress user permissions
- Monitor MCP logs for suspicious activity

## Notes

- The bridge server translates between Kiro's stdio MCP protocol and WordPress's HTTP-based MCP endpoint
- All WordPress functions respect user roles and capabilities
- The AIWU plugin appears as "AI Copilot - Content Generator" in the WordPress plugins list
- MCP functions work with any WordPress content type, custom fields, and taxonomies