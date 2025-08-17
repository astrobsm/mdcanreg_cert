#!/usr/bin/env python3
"""
Deployment Status Check for MDCAN BDM 2025 Platform
Quick health check script for production deployment
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

def check_deployment_status(base_url):
    """Check deployment status with comprehensive tests"""
    print(f"🔍 Checking deployment status for: {base_url}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("-" * 60)
    
    checks = []
    
    # Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            checks.append(("Health Check", "✅ PASS", response.status_code))
            try:
                data = response.json()
                if data.get('status') == 'ok':
                    checks.append(("Health Status", "✅ PASS", "Status OK"))
                else:
                    checks.append(("Health Status", "⚠️ WARN", f"Status: {data.get('status')}"))
            except:
                checks.append(("Health JSON", "⚠️ WARN", "Not JSON response"))
        else:
            checks.append(("Health Check", "❌ FAIL", response.status_code))
    except Exception as e:
        checks.append(("Health Check", "❌ FAIL", str(e)))
    
    # API health check
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            checks.append(("API Health", "✅ PASS", response.status_code))
        else:
            checks.append(("API Health", "❌ FAIL", response.status_code))
    except Exception as e:
        checks.append(("API Health", "❌ FAIL", str(e)))
    
    # Database connection check
    try:
        response = requests.get(f"{base_url}/api/stats", timeout=15)
        if response.status_code == 200:
            checks.append(("Database", "✅ PASS", "Stats endpoint working"))
        else:
            checks.append(("Database", "❌ FAIL", f"Stats endpoint: {response.status_code}"))
    except Exception as e:
        checks.append(("Database", "❌ FAIL", str(e)))
    
    # Frontend serving
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200 and 'html' in response.headers.get('content-type', '').lower():
            checks.append(("Frontend", "✅ PASS", "HTML served"))
        else:
            checks.append(("Frontend", "❌ FAIL", f"Status: {response.status_code}"))
    except Exception as e:
        checks.append(("Frontend", "❌ FAIL", str(e)))
    
    # Registration endpoint
    try:
        # Test with invalid data to check if endpoint exists
        response = requests.post(f"{base_url}/api/register", 
                                json={"test": "invalid"}, 
                                timeout=10)
        if response.status_code in [400, 422]:  # Expected validation error
            checks.append(("Registration", "✅ PASS", "Endpoint exists"))
        elif response.status_code == 404:
            checks.append(("Registration", "❌ FAIL", "Endpoint not found"))
        else:
            checks.append(("Registration", "⚠️ WARN", f"Status: {response.status_code}"))
    except Exception as e:
        checks.append(("Registration", "❌ FAIL", str(e)))
    
    # Print results
    print("\n📊 DEPLOYMENT STATUS REPORT")
    print("=" * 60)
    
    passed = 0
    failed = 0
    warnings = 0
    
    for check_name, status, details in checks:
        print(f"{check_name:20} {status:10} {details}")
        if "✅" in status:
            passed += 1
        elif "❌" in status:
            failed += 1
        else:
            warnings += 1
    
    print("-" * 60)
    print(f"Summary: {passed} passed, {failed} failed, {warnings} warnings")
    
    if failed == 0:
        print("🎉 DEPLOYMENT SUCCESSFUL!")
        return True
    else:
        print("💥 DEPLOYMENT HAS ISSUES - Check failed items above")
        return False

def main():
    # Default to localhost for local testing, or get from environment
    base_url = os.environ.get('APP_URL', 'http://localhost:8080')
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    success = check_deployment_status(base_url)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
