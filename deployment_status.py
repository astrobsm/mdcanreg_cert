#!/usr/bin/env python3
"""
Simple test to check the current deployment status and provide recommendations
"""

import requests
import time

BASE_URL = "https://mdcanbdm042-2025-tdlv8.ondigitalocean.app"

def test_endpoints():
    """Test all available endpoints to see what's working"""
    
    endpoints = [
        ("/api/health", "Health check"),
        ("/api/test", "API test"),
        ("/api/status", "System status"),
        ("/", "Frontend"),
    ]
    
    results = {}
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
            results[endpoint] = {
                "status": response.status_code,
                "description": description,
                "working": response.status_code == 200
            }
            if response.status_code == 200:
                try:
                    data = response.json()
                    results[endpoint]["data"] = data
                except:
                    results[endpoint]["data"] = response.text[:100]
        except Exception as e:
            results[endpoint] = {
                "status": "ERROR",
                "description": description,
                "working": False,
                "error": str(e)
            }
    
    return results

def print_status(results):
    """Print the current status in a readable format"""
    
    print("=" * 60)
    print("MDCAN BDM 2025 - Current Deployment Status")
    print("=" * 60)
    print(f"Testing URL: {BASE_URL}")
    print()
    
    working_count = 0
    total_count = len(results)
    
    for endpoint, result in results.items():
        status_icon = "✅" if result["working"] else "❌"
        print(f"{status_icon} {result['description']}: {result['status']}")
        
        if result["working"]:
            working_count += 1
            if "data" in result and isinstance(result["data"], dict):
                # Print key information from successful responses
                if "database_connected" in result["data"]:
                    print(f"   Database connected: {result['data']['database_connected']}")
                if "status" in result["data"]:
                    print(f"   Status: {result['data']['status']}")
        else:
            if "error" in result:
                print(f"   Error: {result['error'][:50]}...")
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: {working_count}/{total_count} endpoints working")
    print("=" * 60)
    
    if working_count >= 3:
        print("🎉 App is mostly functional!")
        print("✅ Frontend accessible")
        print("✅ Backend API working")
        
        if working_count == total_count:
            print("✅ All systems operational")
        else:
            print("⚠️  Some database operations may be slow or failing")
            print("💡 Try using the web interface for registration")
    else:
        print("⚠️  App may still be deploying or has issues")
        print("💡 Wait a few more minutes and try again")
    
    print(f"\n🌐 Access your app: {BASE_URL}")

if __name__ == "__main__":
    print("Testing deployment status...")
    time.sleep(5)  # Brief wait
    
    results = test_endpoints()
    print_status(results)
    
    print("\n📋 Next Steps:")
    print("1. Try accessing the registration page in your browser")
    print("2. Check Digital Ocean app logs for database connection details")
    print("3. Verify database user credentials in Digital Ocean console")
    print("4. The participant table exists - just need correct authentication")
