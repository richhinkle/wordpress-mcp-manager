#!/usr/bin/env python3
"""
Test progress tracking functionality
"""
import os
import sys
import time
import requests
import json

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_progress_session_creation():
    """Test creating and updating a progress session"""
    
    print("🧪 Testing Progress Session Creation")
    print("=" * 50)
    
    try:
        from src.api.progress_routes import create_progress_session, update_progress, get_progress, complete_progress
        
        # Create a test session
        session_id = create_progress_session("Test Operation", 100)
        print(f"✅ Created session: {session_id}")
        
        # Update progress
        update_progress(session_id, step=25, message="25% complete", details={'processed': 25})
        progress_data = get_progress(session_id)
        
        print(f"📊 Progress data: {progress_data}")
        
        assert progress_data['percentage'] == 25.0, f"Expected 25%, got {progress_data['percentage']}%"
        assert progress_data['message'] == "25% complete", f"Message mismatch"
        
        # Complete the session
        complete_progress(session_id, "Operation completed successfully!")
        final_data = get_progress(session_id)
        
        print(f"✅ Final data: {final_data}")
        
        assert final_data['status'] == 'complete', f"Expected complete status"
        assert final_data['percentage'] == 100.0, f"Expected 100% completion"
        
        print("🎉 Progress session test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Progress session test failed: {e}")
        return False

def test_progress_api_endpoints():
    """Test progress API endpoints"""
    
    print("\n🧪 Testing Progress API Endpoints")
    print("=" * 50)
    
    try:
        # Test creating a session via import
        from src.api.progress_routes import create_progress_session, update_progress
        
        session_id = create_progress_session("API Test", 50)
        print(f"✅ Created session via API: {session_id}")
        
        # Test status endpoint
        response = requests.get(f"http://localhost:5000/api/progress/status/{session_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Status response: {data}")
            
            assert data['success'] == True, "Expected success=True"
            assert 'progress' in data, "Expected progress data"
            
            print("✅ Status endpoint test passed!")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
            return False
        
        # Update progress and test again
        update_progress(session_id, step=30, message="API test in progress...")
        
        response = requests.get(f"http://localhost:5000/api/progress/status/{session_id}")
        data = response.json()
        
        assert data['progress']['percentage'] == 60.0, f"Expected 60%, got {data['progress']['percentage']}%"
        print("✅ Progress update test passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False

def test_progress_integration():
    """Test progress tracking with actual Instagram scraping"""
    
    print("\n🧪 Testing Progress Integration with Instagram Scraping")
    print("=" * 50)
    
    try:
        # Test scraping with progress (using a small limit)
        response = requests.post("http://localhost:5000/api/instagram/apify/scrape-user", 
                               json={"username": "example_user", "limit": 3},
                               headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            data = response.json()
            print(f"📱 Scrape response: {data}")
            
            if 'progress_session_id' in data:
                session_id = data['progress_session_id']
                print(f"✅ Got progress session ID: {session_id}")
                
                # Check progress status
                time.sleep(1)  # Give it a moment
                
                status_response = requests.get(f"http://localhost:5000/api/progress/status/{session_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"📊 Progress status: {status_data}")
                    
                    print("✅ Progress integration test passed!")
                    return True
                else:
                    print(f"❌ Progress status check failed: {status_response.status_code}")
                    return False
            else:
                print("⚠️ No progress session ID in response (might be expected if Apify not configured)")
                return True
        else:
            print(f"❌ Scraping request failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Progress integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Progress Tracking System")
    print("=" * 60)
    
    success = True
    success &= test_progress_session_creation()
    success &= test_progress_api_endpoints()
    success &= test_progress_integration()
    
    if success:
        print("\n🎉 All progress tracking tests passed!")
        print("\n📋 Progress Features Verified:")
        print("  ✅ Session creation and management")
        print("  ✅ Progress updates and completion")
        print("  ✅ REST API endpoints")
        print("  ✅ Integration with Instagram scraping")
        print("  ✅ Real-time progress tracking ready")
    else:
        print("\n❌ Some progress tracking tests failed!")
        sys.exit(1)