#!/usr/bin/env python3
"""
MDCAN BDM 2025 - Final Deployment Verification Script
Comprehensive check of all deployment requirements and configurations.
"""

import os
import sys
import json

def check_environment_variables():
    """Check all required environment variables"""
    print("🔍 CHECKING ENVIRONMENT VARIABLES...")
    
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY', 
        'ADMIN_PASSWORD',
        'EMAIL_HOST',
        'EMAIL_PORT',
        'EMAIL_USERNAME',
        'EMAIL_PASSWORD'
    ]
    
    optional_vars = [
        'PORT',
        'DB_POOL_SIZE',
        'DB_MAX_OVERFLOW',
        'FLASK_ENV',
        'EMAIL_FROM'
    ]
    
    print("   Required Variables:")
    missing_required = []
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            # Hide sensitive values
            display_value = "***" if any(secret in var.lower() for secret in ['password', 'key', 'secret']) else value[:20] + "..." if len(value) > 20 else value
            print(f"      ✅ {var}: {display_value}")
        else:
            print(f"      ❌ {var}: NOT SET")
            missing_required.append(var)
    
    print("\n   Optional Variables:")
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            print(f"      ✅ {var}: {value}")
        else:
            print(f"      ⚠️  {var}: Using default")
    
    return len(missing_required) == 0, missing_required

def check_file_structure():
    """Check critical files exist"""
    print("\n🔍 CHECKING FILE STRUCTURE...")
    
    critical_files = [
        'backend/minimal_app.py',
        'wsgi.py',
        'requirements.txt',
        'Dockerfile',
        '.do/app.yaml',
        'gunicorn.conf.py'
    ]
    
    optional_files = [
        'frontend/public/president-signature.png',
        'frontend/public/chairman-signature.png',
        'frontend/build/index.html'
    ]
    
    print("   Critical Files:")
    missing_critical = []
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"      ✅ {file_path}")
        else:
            print(f"      ❌ {file_path}: MISSING")
            missing_critical.append(file_path)
    
    print("\n   Optional Files:")
    for file_path in optional_files:
        if os.path.exists(file_path):
            print(f"      ✅ {file_path}")
        else:
            print(f"      ⚠️  {file_path}: Missing (may affect functionality)")
    
    return len(missing_critical) == 0, missing_critical

def check_app_import():
    """Test importing the Flask app"""
    print("\n🔍 CHECKING APP IMPORT...")
    
    try:
        # Add current directory and backend to path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        sys.path.insert(0, os.path.join(current_dir, 'backend'))
        
        # Try importing the app
        from backend.minimal_app import app
        print("      ✅ Flask app imports successfully")
        
        # Test app configuration
        with app.app_context():
            print(f"      ✅ App context works")
            print(f"      ✅ App name: {app.name}")
            
        return True, None
        
    except Exception as e:
        print(f"      ❌ App import failed: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)

def check_database_config():
    """Check database configuration"""
    print("\n🔍 CHECKING DATABASE CONFIGURATION...")
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("      ❌ DATABASE_URL not set")
        return False, "DATABASE_URL missing"
    
    # Parse database URL
    try:
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        
        print(f"      ✅ Database scheme: {parsed.scheme}")
        print(f"      ✅ Database host: {parsed.hostname}")
        print(f"      ✅ Database port: {parsed.port}")
        print(f"      ✅ Database name: {parsed.path[1:] if parsed.path else 'N/A'}")
        print(f"      ✅ Database user: {parsed.username}")
        print(f"      ✅ Database password: {'***' if parsed.password else 'N/A'}")
        
        # Check SSL requirement
        if 'sslmode=require' in database_url:
            print("      ✅ SSL mode: Required (recommended for production)")
        else:
            print("      ⚠️  SSL mode: Not explicitly required")
        
        return True, None
        
    except Exception as e:
        print(f"      ❌ Database URL parsing failed: {e}")
        return False, str(e)

def check_docker_config():
    """Check Docker configuration"""
    print("\n🔍 CHECKING DOCKER CONFIGURATION...")
    
    if not os.path.exists('Dockerfile'):
        print("      ❌ Dockerfile missing")
        return False, "Dockerfile missing"
    
    try:
        with open('Dockerfile', 'r') as f:
            dockerfile_content = f.read()
        
        # Check key configurations
        checks = [
            ('python:3.11', 'Python 3.11 base image'),
            ('COPY requirements.txt', 'Requirements copy'),
            ('pip install', 'Pip install'),
            ('gunicorn', 'Gunicorn command'),
            ('EXPOSE 8080', 'Port 8080 exposed'),
        ]
        
        for check_text, description in checks:
            if check_text.lower() in dockerfile_content.lower():
                print(f"      ✅ {description}")
            else:
                print(f"      ⚠️  {description}: Not found")
        
        return True, None
        
    except Exception as e:
        print(f"      ❌ Dockerfile check failed: {e}")
        return False, str(e)

def check_requirements():
    """Check requirements.txt"""
    print("\n🔍 CHECKING REQUIREMENTS...")
    
    if not os.path.exists('requirements.txt'):
        print("      ❌ requirements.txt missing")
        return False, "requirements.txt missing"
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        critical_packages = [
            'Flask',
            'SQLAlchemy',
            'psycopg2',
            'gunicorn',
            'wkhtmltopdf'
        ]
        
        for package in critical_packages:
            if package.lower() in requirements.lower():
                print(f"      ✅ {package}")
            else:
                print(f"      ⚠️  {package}: Not explicitly listed")
        
        return True, None
        
    except Exception as e:
        print(f"      ❌ Requirements check failed: {e}")
        return False, str(e)

def main():
    """Run all deployment checks"""
    print("🚀 MDCAN BDM 2025 - FINAL DEPLOYMENT VERIFICATION")
    print("=" * 60)
    
    all_passed = True
    issues = []
    
    # Run all checks
    checks = [
        ("Environment Variables", check_environment_variables),
        ("File Structure", check_file_structure),
        ("App Import", check_app_import),
        ("Database Config", check_database_config),
        ("Docker Config", check_docker_config),
        ("Requirements", check_requirements)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            passed, error = check_func()
            results[check_name] = {"passed": passed, "error": error}
            
            if not passed:
                all_passed = False
                issues.append(f"{check_name}: {error}")
                
        except Exception as e:
            print(f"\n❌ UNEXPECTED ERROR in {check_name}: {e}")
            all_passed = False
            issues.append(f"{check_name}: Unexpected error - {e}")
            results[check_name] = {"passed": False, "error": f"Unexpected error: {e}"}
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 DEPLOYMENT VERIFICATION SUMMARY")
    print("=" * 60)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"   {status} {check_name}")
        if not result["passed"] and result["error"]:
            print(f"        Error: {result['error']}")
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 ALL CHECKS PASSED! Deployment should be ready.")
        print("\nNext steps:")
        print("1. Commit and push all changes")
        print("2. Redeploy on Digital Ocean")
        print("3. Test all endpoints")
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED. Please address the following issues:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
