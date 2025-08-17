#!/usr/bin/env python3
"""
Pre-deployment verification script
Tests that the application can start successfully
"""
import os
import sys
import tempfile
import subprocess

def test_import():
    """Test that the application can be imported"""
    try:
        print("🧪 Testing application import...")
        from backend.minimal_app import app
        print("✅ Application imports successfully")
        return True
    except Exception as e:
        print(f"❌ Application import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_config():
    """Test database configuration"""
    try:
        print("🧪 Testing database configuration...")
        from backend.minimal_app import app, db
        
        with app.app_context():
            # Try to create engine and connect
            engine = db.engine
            print("✅ Database engine created successfully")
            return True
    except Exception as e:
        print(f"❌ Database configuration failed: {e}")
        return False

def test_gunicorn_config():
    """Test gunicorn configuration"""
    try:
        print("🧪 Testing gunicorn configuration...")
        import gunicorn.config
        
        # Try to load our config
        config_path = "gunicorn.conf.py"
        if os.path.exists(config_path):
            print("✅ Gunicorn config file exists")
            return True
        else:
            print("❌ Gunicorn config file missing")
            return False
    except Exception as e:
        print(f"❌ Gunicorn configuration failed: {e}")
        return False

def test_environment_variables():
    """Test critical environment variables"""
    print("🧪 Testing environment variables...")
    
    required_vars = ['PORT', 'FLASK_ENV']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    else:
        print("✅ Required environment variables present")
        return True

def main():
    """Run all tests"""
    print("🚀 MDCAN BDM 2025 - Pre-deployment Verification")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Application Import", test_import),
        ("Database Configuration", test_database_config),
        ("Gunicorn Configuration", test_gunicorn_config),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Application is ready for deployment.")
        return 0
    else:
        print("💥 Some tests failed. Please fix issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
