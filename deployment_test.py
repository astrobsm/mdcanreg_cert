#!/usr/bin/env python3
"""
Quick deployment validation script for DigitalOcean
Tests minimal functionality to ensure deployment will succeed
"""

import os
import sys

def test_environment_variables():
    """Test that critical environment variables are available"""
    print("🔍 Testing Environment Variables...")
    
    critical_vars = ['PORT', 'DATABASE_URL', 'ADMIN_PASSWORD']
    missing = []
    
    for var in critical_vars:
        value = os.environ.get(var)
        if value:
            if var == 'DATABASE_URL':
                print(f"  ✅ {var}: {value[:30]}...")
            elif var == 'ADMIN_PASSWORD':
                print(f"  ✅ {var}: {'*' * len(value)}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: NOT SET")
            missing.append(var)
    
    return len(missing) == 0

def test_python_imports():
    """Test that all required Python packages can be imported"""
    print("\n📦 Testing Python Imports...")
    
    packages = [
        'flask',
        'flask_sqlalchemy', 
        'flask_cors',
        'psycopg2',
        'gunicorn'
    ]
    
    failed = []
    for package in packages:
        try:
            __import__(package)
            print(f"  ✅ {package}: Available")
        except ImportError as e:
            print(f"  ❌ {package}: {e}")
            failed.append(package)
    
    return len(failed) == 0

def test_app_import():
    """Test that the Flask app can be imported"""
    print("\n🧪 Testing Application Import...")
    
    try:
        # Add backend to path
        backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        
        from backend.minimal_app import app
        print("  ✅ Flask app imported successfully")
        print(f"  ✅ App name: {app.name}")
        return True
    except Exception as e:
        print(f"  ❌ App import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wsgi_import():
    """Test that WSGI module can be imported"""
    print("\n🔧 Testing WSGI Import...")
    
    try:
        import wsgi
        print("  ✅ WSGI module imported successfully")
        print(f"  ✅ Application: {wsgi.application}")
        return True
    except Exception as e:
        print(f"  ❌ WSGI import failed: {e}")
        return False

def main():
    """Run all deployment tests"""
    print("🚀 MDCAN BDM 2025 - Deployment Validation")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Python Imports", test_python_imports),
        ("Application Import", test_app_import),
        ("WSGI Import", test_wsgi_import)
    ]
    
    results = []
    for test_name, test_func in tests:
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Deployment should succeed.")
        return 0
    else:
        print("⚠️ Some tests failed. Deployment may fail.")
        return 1

if __name__ == "__main__":
    exit(main())
