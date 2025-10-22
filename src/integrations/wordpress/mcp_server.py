#!/usr/bin/env python3
"""
Proper MCP Server for WordPress AIWU plugin
"""
import sys
import json
import asyncio
import requests
from typing import Any, Dict

WORDPRESS_URL = "https://your-wordpress-site.com/wp-json/mcp/v1/sse"
ACCESS_TOKEN = "your-access-token-here"

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