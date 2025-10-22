#!/usr/bin/env python3
"""
MCP stdio bridge for WordPress AIWU plugin
"""
import sys
import json
import requests
import threading
import queue
from urllib.parse import urlencode

WORDPRESS_URL = "https://your-wordpress-site.com/wp-json/mcp/v1/sse"
ACCESS_TOKEN = "your-access-token-here"

class WordPressMCPBridge:
    def __init__(self):
        self.request_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
    def handle_mcp_request(self, request):
        """Handle MCP request and forward to WordPress"""
        url = f"{WORDPRESS_URL}?token={ACCESS_TOKEN}"
        
        try:
            # Forward the MCP request to WordPress
            response = requests.post(url, json=request, headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            })
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32000,
                        "message": f"WordPress error: {response.status_code}"
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
                    response = self.handle_mcp_request(request)
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
    bridge = WordPressMCPBridge()
    bridge.run()