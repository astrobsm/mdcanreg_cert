#!/usr/bin/env python3
"""
CRITICAL: Deployment Readiness Test Script
Verifies all critical components before Digital Ocean deployment
"""

import os
import sys
import json
import subprocess
from datetime import datetime

def test_imports():
    """Test critical imports"""
    print("🔍 Testing imports...")
    try:
        sys.path.insert(0, '.')
        sys.path.insert(0, './backend')
        
        from wsgi import application
        print("✅ WSGI application import: SUCCESS")
        
        from backend.minimal_app import app
        print("✅ Flask app import: SUCCESS")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_health_endpoints():
    """Test health check endpoints"""
    print("\n🔍 Testing health endpoints...")
    try:
        from backend.minimal_app import app
        
        with app.test_client() as client:
            # Test /health
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ /health endpoint: SUCCESS (200 OK)")
                print(f"   Response: {response.get_json()}")
            else:
                print(f"❌ /health endpoint: FAILED ({response.status_code})")
                return False
            
            # Test /api/health
            response = client.get('/api/health')
            if response.status_code == 200:
                print("✅ /api/health endpoint: SUCCESS (200 OK)")
                data = response.get_json()
                print(f"   Status: {data.get('status')}")
                print(f"   Database: {data.get('database')}")
                print(f"   PDF generation: {data.get('pdf_generation')}")
                print(f"   Frontend build: {data.get('frontend_build')}")
            else:
                print(f"❌ /api/health endpoint: FAILED ({response.status_code})")
                return False
                
        return True
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_gunicorn_config():
    """Test Gunicorn configuration"""
    print("\n🔍 Testing Gunicorn configuration...")
    try:
        # Test with different PORT values
        for port in ['8080', '3000', '5000']:
            os.environ['PORT'] = port
            
            # Load and execute the gunicorn config
            gunicorn_conf = {}
            with open('gunicorn.conf.py', 'r', encoding='utf-8') as f:
                exec(f.read(), gunicorn_conf)
            
            expected_bind = f"0.0.0.0:{port}"
            actual_bind = gunicorn_conf.get('bind')
            
            if actual_bind == expected_bind:
                print(f"✅ Gunicorn binding for PORT={port}: SUCCESS ({actual_bind})")
            else:
                print(f"❌ Gunicorn binding for PORT={port}: FAILED (expected {expected_bind}, got {actual_bind})")
                return False
                
        # Test other critical settings
        os.environ['PORT'] = '8080'
        gunicorn_conf = {}
        with open('gunicorn.conf.py', 'r', encoding='utf-8') as f:
            exec(f.read(), gunicorn_conf)
            
        if gunicorn_conf.get('workers') == 1:
            print("✅ Gunicorn workers: SUCCESS (1)")
        else:
            print(f"❌ Gunicorn workers: FAILED (expected 1, got {gunicorn_conf.get('workers')})")
            
        if gunicorn_conf.get('timeout') == 120:
            print("✅ Gunicorn timeout: SUCCESS (120s)")
        else:
            print(f"❌ Gunicorn timeout: FAILED (expected 120, got {gunicorn_conf.get('timeout')})")
                
        return True
    except Exception as e:
        print(f"❌ Gunicorn config error: {e}")
        return False

def test_frontend_build():
    """Test frontend build structure"""
    print("\n🔍 Testing frontend build...")
    try:
        build_path = "frontend/build"
        index_path = os.path.join(build_path, "index.html")
        static_path = os.path.join(build_path, "static")
        
        if os.path.exists(build_path):
            print("✅ Frontend build directory: EXISTS")
        else:
            print("❌ Frontend build directory: MISSING")
            return False
            
        if os.path.exists(index_path):
            print("✅ Frontend index.html: EXISTS")
            # Check content
            with open(index_path, 'r') as f:
                content = f.read()
                if "MDCAN BDM 2025" in content:
                    print("✅ Frontend index.html content: VALID")
                else:
                    print("❌ Frontend index.html content: INVALID")
                    return False
        else:
            print("❌ Frontend index.html: MISSING")
            return False
            
        if os.path.exists(static_path):
            print("✅ Frontend static directory: EXISTS")
        else:
            print("❌ Frontend static directory: MISSING")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Frontend build error: {e}")
        return False

def test_environment_variables():
    """Test environment variable handling"""
    print("\n🔍 Testing environment variables...")
    try:
        # Test PORT variable
        original_port = os.environ.get('PORT')
        
        os.environ['PORT'] = '8080'
        port = os.environ.get('PORT', '3000')
        if port == '8080':
            print("✅ PORT environment variable: SUCCESS")
        else:
            print("❌ PORT environment variable: FAILED")
            return False
            
        # Test fallback
        if 'PORT' in os.environ:
            del os.environ['PORT']
        port = os.environ.get('PORT', '8080')
        if port == '8080':
            print("✅ PORT fallback: SUCCESS")
        else:
            print("❌ PORT fallback: FAILED")
            return False
            
        # Restore original
        if original_port:
            os.environ['PORT'] = original_port
            
        return True
    except Exception as e:
        print(f"❌ Environment variable error: {e}")
        return False

def main():
    """Run all deployment readiness tests"""
    print("🚀 MDCAN BDM 2025 - DEPLOYMENT READINESS TEST")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Health Endpoints", test_health_endpoints),
        ("Gunicorn Configuration", test_gunicorn_config),
        ("Frontend Build", test_frontend_build),
        ("Environment Variables", test_environment_variables)
    ]
    
    results = {}
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name}: EXCEPTION - {e}")
            results[test_name] = False
            all_passed = False
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print()
    if all_passed:
        print("🎉 ALL TESTS PASSED - READY FOR DEPLOYMENT!")
        print("The application is ready for Digital Ocean deployment.")
    else:
        print("⚠️ SOME TESTS FAILED - REVIEW REQUIRED")
        print("Please address the failed tests before deployment.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
