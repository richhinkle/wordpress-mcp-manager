#!/usr/bin/env python3
"""
Debug script to test MCP ping response
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

WORDPRESS_URL = os.environ.get('WORDPRESS_URL', 'https://your-wordpress-site.com/wp-json/mcp/v1/sse')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', 'your-access-token-here')

def test_mcp_ping():
    """Test MCP ping directly"""
    
    # Create MCP request
    mcp_request = {
        "jsonrpc": "2.0",
        "id": int(time.time()),
        "method": "tools/call",
        "params": {
            "name": "mcp_ping",
            "arguments": {}
        }
    }
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Debug-WordPress-MCP/1.0'
    })
    
    try:
        url = f"{WORDPRESS_URL}?token={ACCESS_TOKEN}"
        print(f"Making request to: {url}")
        print(f"Request payload: {json.dumps(mcp_request, indent=2)}")
        
        response = session.post(url, json=mcp_request, timeout=30)
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Raw response text: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"\nParsed JSON: {json.dumps(result, indent=2)}")
                
                if 'result' in result:
                    mcp_result = result['result']
                    print(f"\nMCP result type: {type(mcp_result)}")
                    print(f"MCP result: {mcp_result}")
                    
                    # Handle the nested content structure from AIWU MCP
                    if isinstance(mcp_result, dict) and 'content' in mcp_result:
                        content = mcp_result['content']
                        print(f"\nContent type: {type(content)}")
                        print(f"Content: {content}")
                        
                        if isinstance(content, list) and len(content) > 0:
                            first_content = content[0]
                            print(f"\nFirst content type: {type(first_content)}")
                            print(f"First content: {first_content}")
                            
                            if isinstance(first_content, dict) and 'text' in first_content:
                                text_data = first_content['text']
                                print(f"\nText data type: {type(text_data)}")
                                print(f"Text data: {text_data}")
                                
                                # Try to parse as JSON
                                try:
                                    parsed_data = json.loads(text_data)
                                    print(f"\nParsed text data type: {type(parsed_data)}")
                                    print(f"Parsed text data: {parsed_data}")
                                    return parsed_data
                                except json.JSONDecodeError as e:
                                    print(f"\nCould not parse as JSON: {e}")
                                    print(f"Returning text as-is: {text_data}")
                                    return text_data
                    
                    return mcp_result
                    
            except json.JSONDecodeError as e:
                print(f"Could not parse response as JSON: {e}")
                return response.text
        else:
            print(f"HTTP error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Request failed: {e}")
        return None

if __name__ == '__main__':
    result = test_mcp_ping()
    print(f"\n=== FINAL RESULT ===")
    print(f"Type: {type(result)}")
    print(f"Value: {result}")