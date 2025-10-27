import requests
import json
import re
from typing import List, Dict, Optional
from urllib.parse import urlparse
import csv
from datetime import datetime

class InstagramManualImport:
    """
    Manual Instagram import system that works with:
    1. Individual Instagram post URLs
    2. CSV files with post data
    3. Manual data entry
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def import_from_urls(self, urls: List[str]) -> List[Dict]:
        """
        Import Instagram posts from a list of URLs
        Example: ['https://www.instagram.com/p/ABC123/', ...]
        """
        posts = []
        
        for url in urls:
            print(f"Processing URL: {url}")
            post_data = self.extract_from_url(url)
            if post_data:
                posts.append(post_data)
                print(f"✅ Extracted: {post_data['caption'][:50]}...")
            else:
                print(f"❌ Failed to extract from: {url}")
        
        return posts
    
    def extract_from_url(self, url: str) -> Optional[Dict]:
        """
        Extract basic information from an Instagram post URL
        """
        try:
            # Extract shortcode from URL
            shortcode_match = re.search(r'/p/([A-Za-z0-9_-]+)/', url)
            if not shortcode_match:
                print(f"Invalid Instagram URL format: {url}")
                return None
            
            shortcode = shortcode_match.group(1)
            
            # Try to get the page
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                # Extract basic info from HTML
                html = response.text
                
                # Try to find image URL
                img_match = re.search(r'"display_url":"([^"]+)"', html)
                image_url = img_match.group(1).replace('\\u0026', '&') if img_match else ''
                
                # Try to find caption
                caption_match = re.search(r'"caption":"([^"]*)"', html)
                caption = caption_match.group(1) if caption_match else ''
                
                # Clean up caption (remove escape characters)
                caption = caption.replace('\\n', '\n').replace('\\"', '"').replace('\\/', '/')
                
                # Extract hashtags
                hashtags = re.findall(r'#(\w+)', caption) if caption else []
                
                post_data = {
                    'id': shortcode,
                    'shortcode': shortcode,
                    'caption': caption,
                    'image_url': image_url,
                    'post_url': url,
                    'hashtags': hashtags,
                    'timestamp': int(datetime.now().timestamp()),
                    'date_posted': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'extraction_method': 'url_scraping'
                }
                
                return post_data
            
        except Exception as e:
            print(f"Error extracting from URL {url}: {e}")
        
        return None
    
    def import_from_csv(self, csv_file: str) -> List[Dict]:
        """
        Import posts from a CSV file
        Expected columns: caption, image_url, post_url, hashtags (optional)
        """
        posts = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for i, row in enumerate(reader):
                    post_data = {
                        'id': f"csv_import_{i}",
                        'shortcode': f"csv_import_{i}",
                        'caption': row.get('caption', ''),
                        'image_url': row.get('image_url', ''),
                        'post_url': row.get('post_url', ''),
                        'hashtags': row.get('hashtags', '').split(',') if row.get('hashtags') else [],
                        'timestamp': int(datetime.now().timestamp()),
                        'date_posted': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'extraction_method': 'csv_import'
                    }
                    posts.append(post_data)
                    print(f"✅ Imported from CSV: {post_data['caption'][:50]}...")
        
        except Exception as e:
            print(f"Error reading CSV file: {e}")
        
        return posts
    
    def create_sample_csv(self, filename: str = 'instagram_import_template.csv'):
        """Create a sample CSV template for manual data entry"""
        sample_data = [
            {
                'caption': 'Sample Instagram post caption with #hashtags #example',
                'image_url': 'https://example.com/image1.jpg',
                'post_url': 'https://www.instagram.com/p/ABC123/',
                'hashtags': 'hashtags,example'
            },
            {
                'caption': 'Another sample post for Example Business #example_business #signs',
                'image_url': 'https://example.com/image2.jpg', 
                'post_url': 'https://www.instagram.com/p/DEF456/',
                'hashtags': 'example_business,signs'
            }
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['caption', 'image_url', 'post_url', 'hashtags'])
            writer.writeheader()
            writer.writerows(sample_data)
        
        print(f"✅ Created sample CSV template: {filename}")
        return filename
    
    def manual_entry(self) -> Dict:
        """Interactive manual entry for a single post"""
        print("\n📝 Manual Instagram Post Entry")
        print("-" * 40)
        
        caption = input("Caption: ")
        image_url = input("Image URL: ")
        post_url = input("Instagram Post URL (optional): ")
        hashtags_str = input("Hashtags (comma-separated, optional): ")
        
        hashtags = [tag.strip() for tag in hashtags_str.split(',') if tag.strip()]
        
        post_data = {
            'id': f"manual_{int(datetime.now().timestamp())}",
            'shortcode': f"manual_{int(datetime.now().timestamp())}",
            'caption': caption,
            'image_url': image_url,
            'post_url': post_url,
            'hashtags': hashtags,
            'timestamp': int(datetime.now().timestamp()),
            'date_posted': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'extraction_method': 'manual_entry'
        }
        
        return post_data

def demo_manual_import():
    """Demonstrate the manual import system"""
    importer = InstagramManualImport()
    
    print("=" * 60)
    print("Instagram Manual Import System Demo")
    print("=" * 60)
    
    # Create sample CSV template
    print("\n1. Creating sample CSV template...")
    template_file = importer.create_sample_csv()
    
    # Demo URL import (with sample URLs for example_user)
    print("\n2. Demo URL Import...")
    sample_urls = [
        "https://www.instagram.com/p/sample1/",  # These would be real URLs
        "https://www.instagram.com/p/sample2/",
    ]
    
    print("Sample URLs to try (replace with real Instagram post URLs):")
    for url in sample_urls:
        print(f"  - {url}")
    
    # Demo CSV import
    print(f"\n3. Demo CSV Import from {template_file}...")
    csv_posts = importer.import_from_csv(template_file)
    
    if csv_posts:
        print(f"✅ Imported {len(csv_posts)} posts from CSV")
        
        # Save results
        with open('manual_import_results.json', 'w', encoding='utf-8') as f:
            json.dump(csv_posts, f, indent=2, ensure_ascii=False)
        print("💾 Saved results to manual_import_results.json")
    
    print("\n" + "=" * 60)
    print("Manual Import Options:")
    print("1. Edit the CSV template with real Instagram data")
    print("2. Use individual Instagram post URLs")
    print("3. Manual entry through the interactive prompt")
    print("4. Integrate with your WordPress MCP Manager")
    print("=" * 60)

if __name__ == "__main__":
    demo_manual_import()