#!/usr/bin/env python
"""
This script verifies that the application can start with the correct port configuration.
It simulates how Digital Ocean will run the application.
"""
import os
import sys
import subprocess
import time
import requests

# First, let's test the app with different PORT values
test_cases = [
    {"PORT": "8080"},
    {"PORT": "$PORT"},  # This should be handled correctly
    {}  # No PORT set
]

# Function to run the docker startup script
def run_app(env_vars=None):
    if env_vars is None:
        env_vars = {}
    
    # Create a copy of the current environment
    env = os.environ.copy()
    
    # Add our test environment variables
    for key, value in env_vars.items():
        env[key] = value
    
    print(f"\n🔍 Testing with environment: {env_vars}")
    
    # Run the app in the background
    process = subprocess.Popen(
        ["python", "do_app.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give it a moment to start
    time.sleep(2)
    
    # Check if the process is still running
    if process.poll() is not None:
        print("❌ Process terminated unexpectedly")
        stdout, stderr = process.communicate()
        print("STDOUT:")
        print(stdout)
        print("STDERR:")
        print(stderr)
        return False
    
    # Test if the app is responding
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        print(f"✅ App responded with status code: {response.status_code}")
        print(f"Response: {response.text}")
        success = response.status_code == 200
    except Exception as e:
        print(f"❌ Error connecting to app: {str(e)}")
        success = False
    
    # Terminate the process
    process.terminate()
    process.wait()
    
    return success

# Run the tests
success = True
for env_vars in test_cases:
    if not run_app(env_vars):
        success = False

if success:
    print("\n✅ All tests passed! The app should work correctly on Digital Ocean.")
    sys.exit(0)
else:
    print("\n❌ Some tests failed. Please check the issues above.")
    sys.exit(1)
