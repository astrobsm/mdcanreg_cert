#!/usr/bin/env python3
"""
Test script to check specific certificate endpoints and error details
"""
import requests
import json

def test_certificate_endpoints():
    """Test certificate-related endpoints"""
    base_url = "https://douglas-app-hwqj3.ondigitalocean.app"
    
    print("🧪 Testing certificate endpoints...")
    
    # First, get health status
    try:
        health_response = requests.get(f"{base_url}/api/health", timeout=30)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"\n📊 Health Check:")
            print(f"   PDF Generation: {health_data.get('pdf_generation', 'unknown')}")
            print(f"   Database: {health_data.get('database', 'unknown')}")
            print(f"   Environment: {health_data.get('environment', 'unknown')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Get participants to find valid IDs
    try:
        participants_response = requests.get(f"{base_url}/api/participants", timeout=30)
        if participants_response.status_code == 200:
            participants_data = participants_response.json()
            participants = participants_data.get('participants', [])
            print(f"\n👥 Found {len(participants)} participants")
            
            if participants:
                # Test with first participant
                participant_id = participants[0].get('id')
                participant_name = participants[0].get('name', 'Unknown')
                print(f"   Testing with participant: {participant_name} (ID: {participant_id})")
                
                # Test certificate generation (GET - no email)
                try:
                    test_url = f"{base_url}/api/test-certificate/{participant_id}"
                    print(f"\n🔍 Testing certificate generation: {test_url}")
                    
                    test_response = requests.get(test_url, timeout=30)
                    print(f"   Status: {test_response.status_code}")
                    print(f"   Content-Type: {test_response.headers.get('Content-Type', 'N/A')}")
                    
                    if test_response.status_code == 200:
                        print("   ✅ Certificate generation working")
                        try:
                            response_data = test_response.json()
                            print(f"   📄 Response keys: {list(response_data.keys())}")
                        except:
                            print(f"   📄 Response length: {len(test_response.content)} bytes")
                    else:
                        print(f"   ❌ Certificate generation failed: {test_response.text[:200]}")
                        
                except Exception as e:
                    print(f"   ❌ Certificate test error: {e}")
                
                # Test certificate sending (POST - with email)
                try:
                    send_url = f"{base_url}/api/send-certificate/{participant_id}"
                    print(f"\n🔍 Testing certificate sending: {send_url}")
                    
                    send_response = requests.post(send_url, timeout=30)
                    print(f"   Status: {send_response.status_code}")
                    print(f"   Content-Type: {send_response.headers.get('Content-Type', 'N/A')}")
                    
                    if send_response.status_code == 200:
                        print("   ✅ Certificate sending working")
                        try:
                            response_data = send_response.json()
                            print(f"   📄 Response keys: {list(response_data.keys())}")
                        except:
                            print(f"   📄 Response length: {len(send_response.content)} bytes")
                    else:
                        print(f"   ❌ Certificate sending failed: {send_response.text[:500]}")
                        
                except Exception as e:
                    print(f"   ❌ Certificate send error: {e}")
            else:
                print("   ⚠️ No participants found to test with")
                
    except Exception as e:
        print(f"❌ Participants check failed: {e}")
    
    print("\n🏁 Certificate testing complete")

if __name__ == "__main__":
    test_certificate_endpoints()
