#!/usr/bin/env python3
"""
Sanitize PII from codebase before git commit
"""
import os
import re
from pathlib import Path

def sanitize_file(file_path, replacements):
    """Apply sanitization replacements to a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for pattern, replacement in replacements.items():
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Sanitized: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error sanitizing {file_path}: {e}")
        return False

def main():
    """Sanitize PII from all tracked files"""
    
    # Define PII replacements
    replacements = {
        r'example_user': 'example_user',
        r'example_business': 'example_business',
        r'Example Business': 'Example Business',
        r'signsoffall\.com': 'your-site.com',
        r'[REDACTED-TOKEN]': '[REDACTED-TOKEN]',
        r'[REDACTED-APIFY-TOKEN]': '[REDACTED-APIFY-TOKEN]',
    }
    
    # File extensions to process
    extensions = {'.py', '.js', '.md', '.html', '.css', '.json', '.txt'}
    
    # Directories to skip
    skip_dirs = {'venv', '.git', '__pycache__', 'node_modules', 'cache'}
    
    sanitized_count = 0
    
    print("🧹 Sanitizing PII from codebase...")
    print("=" * 50)
    
    for root, dirs, files in os.walk('.'):
        # Skip unwanted directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            file_path = Path(root) / file
            
            # Only process files with relevant extensions
            if file_path.suffix in extensions:
                if sanitize_file(file_path, replacements):
                    sanitized_count += 1
    
    print(f"\n🎉 Sanitization complete! Modified {sanitized_count} files")
    print("\n⚠️  Remember to:")
    print("1. Review changes with 'git diff'")
    print("2. Regenerate all exposed credentials")
    print("3. Update .env with new credentials (not committed)")

if __name__ == "__main__":
    main()