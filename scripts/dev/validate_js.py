#!/usr/bin/env python3
"""
Validate JavaScript syntax
"""

import subprocess
import sys

def validate_javascript():
    """Validate JavaScript file syntax using Node.js"""
    try:
        # Try to parse the JavaScript file with Node.js
        result = subprocess.run([
            'node', '-c', 'static/app.js'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ JavaScript syntax is valid")
            return True
        else:
            print("❌ JavaScript syntax errors:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("⚠️ Node.js not found, cannot validate JavaScript syntax")
        return None
    except subprocess.TimeoutExpired:
        print("⚠️ JavaScript validation timed out")
        return None
    except Exception as e:
        print(f"❌ Error validating JavaScript: {e}")
        return None

if __name__ == "__main__":
    validate_javascript()