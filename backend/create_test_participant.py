import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8080/api"

# Test data for a participant
participant_data = {
    "name": f"Test User {datetime.now().strftime('%Y%m%d%H%M%S')}",
    "email": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
    "organization": "Test Organization",
    "position": "Test Position",
    "phone_number": "1234567890",
    "registration_type": "full",
    "registration_status": "confirmed",
    "registration_fee_paid": True,
    "payment_reference": "TEST-PAYMENT-REF",
    "dietary_requirements": "None",
    "special_needs": "None",
    "emergency_contact_name": "Emergency Contact",
    "emergency_contact_phone": "9876543210",
    "email_notifications": True,
    "sms_notifications": False,
    "certificate_type": "participation"
}

def create_test_participant():
    """Create a test participant and return the result"""
    url = f"{API_BASE_URL}/participants"
    
    try:
        print(f"Creating test participant: {participant_data['name']} ({participant_data['email']})")
        response = requests.post(url, json=participant_data, timeout=10)
        
        if response.status_code == 200 or response.status_code == 201:
            print(f"SUCCESS: Participant created with status code {response.status_code}")
            try:
                print(f"Response data: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"Response content: {response.content}")
            return 0
        else:
            print(f"FAILED: Could not create participant. Status code: {response.status_code}")
            try:
                print(f"Error: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"Response content: {response.content}")
            return 1
    except requests.exceptions.RequestException as e:
        print(f"FAILED: Request failed: {str(e)}")
        return 1
    except Exception as e:
        print(f"FAILED: Test failed: {str(e)}")
        return 1

if __name__ == "__main__":
    create_test_participant()
