"""
Verification script to check if the application (main or minimal) 
is ready for deployment with all necessary features.
"""
import requests
import sys
import time
import json

def check_endpoint(base_url, endpoint, method="GET", data=None, expected_status=200):
    """Test a specific API endpoint and return result"""
    url = f"{base_url}{endpoint}"
    print(f"Testing {method} {url}...")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            return False, f"Unsupported method: {method}"
            
        if response.status_code != expected_status:
            return False, f"Expected status {expected_status}, got {response.status_code}. Response: {response.text}"
            
        try:
            response_data = response.json()
            return True, response_data
        except:
            return True, response.text
    except Exception as e:
        return False, str(e)

def run_verification(base_url):
    """Run a comprehensive verification of all API endpoints"""
    print(f"Running verification against {base_url}")
    print("=" * 80)
    
    all_checks_passed = True
    
    # Basic health check
    success, result = check_endpoint(base_url, "/api/health")
    if not success:
        print(f"❌ Health check failed: {result}")
        return False
    print(f"✅ Health check passed: {result}")
    
    # API test endpoint
    success, result = check_endpoint(base_url, "/api/test")
    if not success:
        print(f"❌ API test failed: {result}")
        all_checks_passed = False
    else:
        print(f"✅ API test passed: {result}")
    
    # Status endpoint
    success, result = check_endpoint(base_url, "/api/status")
    if not success:
        print(f"❌ Status check failed: {result}")
        all_checks_passed = False
    else:
        print(f"✅ Status check passed: {result}")
        
    # Participant endpoints
    # Create a test participant
    test_participant = {
        "name": "Test User",
        "email": "test@example.com",
        "role": "Attendee",
        "cert_type": "participation",
        "phone": "1234567890",
        "gender": "Other",
        "specialty": "Test",
        "state": "Test State",
        "hospital": "Test Hospital"
    }
    
    success, result = check_endpoint(
        base_url, 
        "/api/participants", 
        method="POST", 
        data=test_participant,
        expected_status=201
    )
    
    if not success:
        print(f"❌ Participant creation failed: {result}")
        all_checks_passed = False
    else:
        print(f"✅ Participant creation passed: {result}")
        
        # Get the created participant ID
        participant_id = result.get("participant", {}).get("id")
        
        if participant_id:
            # Test getting a single participant
            success, result = check_endpoint(base_url, f"/api/participants/{participant_id}")
            if not success:
                print(f"❌ Get participant failed: {result}")
                all_checks_passed = False
            else:
                print(f"✅ Get participant passed: {result}")
            
            # Test updating a participant
            update_data = {"role": "Updated Role"}
            success, result = check_endpoint(
                base_url, 
                f"/api/participants/{participant_id}", 
                method="PUT", 
                data=update_data
            )
            
            if not success:
                print(f"❌ Update participant failed: {result}")
                all_checks_passed = False
            else:
                print(f"✅ Update participant passed: {result}")
            
            # Test certificate generation
            success, result = check_endpoint(
                base_url, 
                f"/api/certificates/{participant_id}"
            )
            
            if not success:
                print(f"❌ Certificate generation failed: {result}")
                all_checks_passed = False
            else:
                print(f"✅ Certificate generation endpoint accessible")
            
            # Cleanup - delete the test participant
            success, result = check_endpoint(
                base_url, 
                f"/api/participants/{participant_id}", 
                method="DELETE"
            )
            
            if not success:
                print(f"❌ Delete participant failed: {result}")
                all_checks_passed = False
            else:
                print(f"✅ Delete participant passed: {result}")
    
    # Test participants list endpoint
    success, result = check_endpoint(base_url, "/api/participants")
    if not success:
        print(f"❌ List participants failed: {result}")
        all_checks_passed = False
    else:
        print(f"✅ List participants passed: {result}")
    
    # Test statistics endpoint
    success, result = check_endpoint(base_url, "/api/statistics")
    if not success:
        print(f"❌ Statistics endpoint failed: {result}")
        all_checks_passed = False
    else:
        print(f"✅ Statistics endpoint passed: {result}")
    
    # Final result
    print("=" * 80)
    if all_checks_passed:
        print("✅ All checks passed! The application is ready for deployment.")
    else:
        print("❌ Some checks failed. Please fix the issues before deployment.")
    
    return all_checks_passed

if __name__ == "__main__":
    # Default to localhost if not specified
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    # Allow some time for the server to start
    print(f"Waiting 3 seconds for the server to be fully ready...")
    time.sleep(3)
    
    success = run_verification(base_url)
    sys.exit(0 if success else 1)
