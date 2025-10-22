#!/usr/bin/env python3
"""
Development server runner for WordPress MCP Manager
"""

import os

# Try to load .env file if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("📄 Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment variables")
    print("💡 Install with: pip install python-dotenv")

# Import and run the Flask app
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from src.core.app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting WordPress MCP Manager on http://localhost:{port}")
    print(f"📝 Debug mode: {'ON' if debug else 'OFF'}")
    
    # Check required environment variables
    wordpress_url = os.environ.get('WORDPRESS_URL')
    access_token = os.environ.get('ACCESS_TOKEN')
    
    if not wordpress_url or not access_token:
        print("❌ Missing required environment variables:")
        print("   WORDPRESS_URL and ACCESS_TOKEN must be set")
        print("   Either create a .env file or set them in your system")
        exit(1)
    
    print(f"🌐 WordPress URL: {wordpress_url}")
    print(f"🔑 Access token: {'*' * (len(access_token) - 4) + access_token[-4:] if access_token else 'NOT SET'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)