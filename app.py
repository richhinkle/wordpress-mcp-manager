#!/usr/bin/env python3
"""
Main entry point for WordPress MCP Manager
Imports and runs the core application
"""

import sys
import os

# Add current directory to Python path for absolute imports
sys.path.insert(0, os.path.dirname(__file__))

# Import and run the main application
from src.core.app import app

if __name__ == '__main__':
    # Configuration check
    WORDPRESS_URL = os.environ.get('WORDPRESS_URL', 'https://your-wordpress-site.com/wp-json/mcp/v1/sse')
    ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', 'your-access-token-here')
    
    if not WORDPRESS_URL or not ACCESS_TOKEN:
        print("Missing required environment variables: WORDPRESS_URL, ACCESS_TOKEN")
        sys.exit(1)
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"Starting WordPress Manager on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)