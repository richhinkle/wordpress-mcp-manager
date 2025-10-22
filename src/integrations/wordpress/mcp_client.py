#!/usr/bin/env python3
"""
WordPress AIWU MCP Client Bridge
"""
import sys
import json
import requests

WORDPRESS_URL = "https://your-wordpress-site.com/wp-json/mcp/v1/sse"
ACCESS_TOKEN = "your-access-token-here"

def handle_mcp_request(request):
    """Handle MCP request and forward to WordPress"""
    url = f"{WORDPRESS_URL}?token={ACCESS_TOKEN}"
    
    try:
        # Forward the MCP request to WordPress
        response = requests.get(url, headers={
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
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
                    "message": f"WordPress error: {response.status_code} - {response.text}"
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

def main():
    """Main stdio loop"""
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
                
            try:
                request = json.loads(line)
                response = handle_mcp_request(request)
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
        print(f"Bridge error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()