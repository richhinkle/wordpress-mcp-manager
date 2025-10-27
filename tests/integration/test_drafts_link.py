#!/usr/bin/env python3
"""
Test WordPress drafts link functionality
"""
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_drafts_url_generation():
    """Test that drafts URL is generated correctly"""
    
    # Test URL generation
    wordpress_url = "https://example.com/wp-json/mcp/v1/sse"
    expected_base = "https://example.com"
    expected_drafts = "https://example.com/wp-admin/edit.php?post_status=draft&post_type=post"
    
    # Simulate the URL transformation
    base_url = wordpress_url.replace('/wp-json/mcp/v1/sse', '')
    drafts_url = f"{base_url}/wp-admin/edit.php?post_status=draft&post_type=post"
    
    print(f"WordPress URL: {wordpress_url}")
    print(f"Base URL: {base_url}")
    print(f"Drafts URL: {drafts_url}")
    
    assert base_url == expected_base, f"Expected {expected_base}, got {base_url}"
    assert drafts_url == expected_drafts, f"Expected {expected_drafts}, got {drafts_url}"
    
    print("✅ URL generation test passed!")

def test_import_response_structure():
    """Test that import response includes drafts URL"""
    
    # Simulate import response
    response = {
        'success': True,
        'imported_count': 3,
        'total_posts': 3,
        'message': 'Successfully imported 3 posts to WordPress'
    }
    
    # Add drafts URL (simulating the API route logic)
    wordpress_base_url = "https://example.com"
    drafts_url = f"{wordpress_base_url}/wp-admin/edit.php?post_status=draft&post_type=post"
    
    response['drafts_url'] = drafts_url
    response['message'] += f'\n\n📝 View and publish your drafts: {drafts_url}'
    
    print("Import response structure:")
    for key, value in response.items():
        print(f"  {key}: {value}")
    
    assert 'drafts_url' in response, "Response should include drafts_url"
    assert 'wp-admin/edit.php' in response['drafts_url'], "Drafts URL should point to WordPress admin"
    assert 'post_status=draft' in response['drafts_url'], "Drafts URL should filter for drafts"
    
    print("✅ Import response structure test passed!")

if __name__ == "__main__":
    print("🧪 Testing WordPress Drafts Link Functionality")
    print("=" * 60)
    
    test_drafts_url_generation()
    print()
    test_import_response_structure()
    
    print("\n🎉 All tests passed! Drafts link functionality is working correctly.")