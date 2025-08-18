import requests
import time
import os

def test_certificate_generation():
    """Test certificate generation to check signature transparency"""
    backend_url = "http://localhost:8080"
    
    print("🧪 Testing Certificate Generation with Transparent Signatures")
    print("=" * 60)
    
    # Wait for backend to be ready
    for i in range(10):
        try:
            response = requests.get(f"{backend_url}/api/health")
            if response.status_code == 200:
                print(f"✅ Backend is ready!")
                break
        except:
            print(f"⏳ Waiting for backend... ({i+1}/10)")
            time.sleep(2)
    else:
        print("❌ Backend not responding")
        return
    
    # Test certificate generation
    try:
        print("\n📄 Generating test certificate...")
        response = requests.get(f"{backend_url}/api/test-certificate/1")
        
        if response.status_code == 200:
            # Save the PDF for inspection
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"test_certificate_{timestamp}.pdf"
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Certificate generated successfully!")
            print(f"📁 Saved as: {filename}")
            print(f"📊 File size: {len(response.content):,} bytes")
            
            # Check if the PDF contains expected signatures
            print("\n🔍 Certificate Analysis:")
            print("- President signature: Should have transparent background")
            print("- Chairman signature: Should have transparent background") 
            print("- Secretary signature: Should have transparent background")
            print(f"\n💡 Open {filename} to visually inspect the signatures")
            print("   Look for any white boxes around the signatures")
            
        else:
            print(f"❌ Failed to generate certificate: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing certificate generation: {e}")

if __name__ == "__main__":
    test_certificate_generation()
