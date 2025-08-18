#!/usr/bin/env python3
"""
Test script to verify API endpoints
"""
import requests
import json

def test_api_endpoints():
    """Test the API endpoints that are failing"""
    base_url = "https://douglas-app-hwqj3.ondigitalocean.app"
    
    endpoints_to_test = [
        "/api/participants",
        "/api/programs", 
        "/api/notifications",
        "/api/stats",
        "/api/health"
    ]
    
    print("🧪 Testing API endpoints...")
    
    for endpoint in endpoints_to_test:
        try:
            url = base_url + endpoint
            print(f"\n🔍 Testing: {url}")
            
            response = requests.get(url, timeout=30)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"   Content-Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS")
                # Try to parse JSON response
                try:
                    json_data = response.json()
                    if isinstance(json_data, list):
                        print(f"   📄 Response: Array with {len(json_data)} items")
                    elif isinstance(json_data, dict):
                        print(f"   📄 Response: Object with keys: {list(json_data.keys())}")
                except:
                    print(f"   📄 Response: {response.text[:100]}...")
            else:
                print(f"   ❌ FAILED: {response.text[:200]}")
                
        except requests.RequestException as e:
            print(f"   ❌ ERROR: {e}")
    
    print("\n🏁 API testing complete")

if __name__ == "__main__":
    test_api_endpoints()
