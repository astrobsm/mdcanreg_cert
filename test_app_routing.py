#!/usr/bin/env python3
"""
Test script to verify app routing locally
"""
import requests
import sys

def test_local_app():
    """Test the local app routing"""
    base_url = "http://localhost:8080"
    
    endpoints_to_test = [
        "/",
        "/api/health",
        "/static/js/main.11da706c.js",
        "/static/css/main.1917ae80.css"
    ]
    
    print("🧪 Testing local app routing...")
    
    for endpoint in endpoints_to_test:
        try:
            url = base_url + endpoint
            print(f"\n🔍 Testing: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"   Content-Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS")
            else:
                print(f"   ❌ FAILED: {response.text[:100]}")
                
        except requests.RequestException as e:
            print(f"   ❌ ERROR: {e}")
    
    print("\n🏁 Local testing complete")

def test_production_app():
    """Test the production app routing"""
    base_url = "https://douglas-app-hwqj3.ondigitalocean.app"
    
    endpoints_to_test = [
        "/",
        "/api/health",
        "/static/js/main.11da706c.js",
        "/static/css/main.1917ae80.css"
    ]
    
    print("🌐 Testing production app routing...")
    
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
            else:
                print(f"   ❌ FAILED: {response.text[:100]}")
                
        except requests.RequestException as e:
            print(f"   ❌ ERROR: {e}")
    
    print("\n🏁 Production testing complete")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "local":
        test_local_app()
    else:
        test_production_app()
