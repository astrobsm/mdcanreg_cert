import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Backend URL
BACKEND_URL = "http://localhost:8080"

def test_api_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/health")
        if response.status_code == 200:
            print(f"✅ API Health check successful: {response.status_code}")
            return True
        else:
            print(f"❌ API Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Health check error: {e}")
        return False

def test_all_endpoints():
    """Test all available API endpoints"""
    endpoints = [
        {"method": "GET", "url": "/api/health", "name": "Health Check"},
        {"method": "GET", "url": "/api/stats", "name": "Statistics"},
        {"method": "GET", "url": "/api/participants", "name": "Get Participants"},
        {"method": "GET", "url": "/api/participants/count", "name": "Count Participants"},
        {"method": "GET", "url": "/api/programs", "name": "Get Programs"},
        {"method": "GET", "url": "/api/announcements", "name": "Get Announcements"},
        {"method": "GET", "url": "/api/materials", "name": "Get Materials"},
    ]
    
    results = []
    for endpoint in endpoints:
        try:
            if endpoint["method"] == "GET":
                response = requests.get(f"{BACKEND_URL}{endpoint['url']}")
            else:
                print(f"⚠️ Method {endpoint['method']} not implemented for testing")
                continue
                
            if response.status_code < 400:
                print(f"✅ {endpoint['name']} ({endpoint['url']}): {response.status_code}")
                results.append({
                    "endpoint": endpoint['url'],
                    "status": "success",
                    "code": response.status_code
                })
            else:
                print(f"❌ {endpoint['name']} ({endpoint['url']}): {response.status_code}")
                results.append({
                    "endpoint": endpoint['url'],
                    "status": "failed",
                    "code": response.status_code,
                    "error": response.text
                })
        except Exception as e:
            print(f"❌ {endpoint['name']} ({endpoint['url']}): Error - {e}")
            results.append({
                "endpoint": endpoint['url'],
                "status": "error",
                "message": str(e)
            })
    
    return results

def save_test_results(results):
    """Save test results to a file"""
    with open("api_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"✅ Test results saved to api_test_results.json")

def main():
    print("===== Testing API endpoints =====")
    if not test_api_health():
        print("❌ API health check failed. Make sure the backend server is running.")
        sys.exit(1)
    
    results = test_all_endpoints()
    save_test_results(results)
    
    # Summary
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\n===== Summary =====")
    print(f"Total endpoints tested: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(results) - success_count}")
    
    if success_count == len(results):
        print("✅ All endpoints are working!")
    else:
        print("⚠️ Some endpoints failed. Check api_test_results.json for details.")

if __name__ == "__main__":
    main()
