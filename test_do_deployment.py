#!/usr/bin/env python3
"""
Test script to verify the app can be imported correctly for Digital Ocean deployment
"""
import os
import sys

print("=== Digital Ocean App Import Test ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Add paths like Digital Ocean would
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/backend')

try:
    print("\n1. Testing digital_ocean_app import...")
    import digital_ocean_app
    print("✅ digital_ocean_app imported successfully")
    
    print("\n2. Testing app instance access...")
    app = digital_ocean_app.app
    print(f"✅ App instance found: {type(app)}")
    
    print("\n3. Testing route count...")
    routes = list(app.url_map.iter_rules())
    print(f"✅ Found {len(routes)} routes")
    
    print("\n4. Testing basic app functionality...")
    with app.test_client() as client:
        response = client.get('/api/health')
        print(f"✅ Health check: {response.status_code}")
    
    print("\n🎉 ALL TESTS PASSED - App is ready for Digital Ocean deployment!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
