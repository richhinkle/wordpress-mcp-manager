#!/usr/bin/env python3
"""
WordPress MCP Server - Bridge to AIWU WordPress Plugin
This creates an MCP server that connects to your WordPress AIWU plugin
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WordPressMCPServer:
    def __init__(self):
        self.wordpress_url = os.getenv('WORDPRESS_URL', 'https://signsoffall.com/wp-json/mcp/v1/sse')
        self.access_token = os.getenv('ACCESS_TOKEN', '')
        
        if not self.access_token:
            raise ValueError("ACCESS_TOKEN not found in environment variables")
    
    async def call_wordpress_mcp(self, method: str, params: Dict[str, Any] = None) -> Any:
        """Call the WordPress MCP plugin"""
        if params is None:
            params = {}
        
        request_data = {
            "method": method,
            "params": params,
            "access_token": self.access_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.wordpress_url,
                json=request_data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests"""
        try:
            method = request.get('method')
            params = request.get('params', {})
            
            # Map MCP methods to WordPress plugin methods
            if method == 'tools/list':
                return {
                    "tools": [
                        {
                            "name": "wp_get_posts",
                            "description": "Get WordPress posts",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "limit": {"type": "number"},
                                    "status": {"type": "string"}
                                }
                            }
                        },
                        {
                            "name": "wp_create_post",
                            "description": "Create WordPress post",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "content": {"type": "string"},
                                    "status": {"type": "string"}
                                },
                                "required": ["title", "content"]
                            }
                        }
                    ]
                }
            
            elif method == 'tools/call':
                tool_name = params.get('name')
                tool_args = params.get('arguments', {})
                
                # Call WordPress MCP plugin
                result = await self.call_wordpress_mcp(tool_name, tool_args)
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            
            else:
                return {"error": f"Unknown method: {method}"}
                
        except Exception as e:
            return {"error": str(e)}

async def main():
    """Main MCP server loop"""
    server = WordPressMCPServer()
    
    # Simple stdio-based MCP server
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
                
            request = json.loads(line.strip())
            response = await server.handle_request(request)
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except Exception as e:
            error_response = {"error": str(e)}
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())