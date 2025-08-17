#!/usr/bin/env python3
"""
Digital Ocean Startup Diagnostic Script
Comprehensive diagnostics for deployment issues
"""

import os
import sys
import logging
import json
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def log_section(title):
    """Log a section header"""
    logger.info("=" * 60)
    logger.info(f"🔍 {title}")
    logger.info("=" * 60)

def check_environment():
    """Check all environment variables"""
    log_section("ENVIRONMENT VARIABLES CHECK")
    
    required_vars = [
        'DATABASE_URL', 'SECRET_KEY', 'ADMIN_PASSWORD', 
        'EMAIL_HOST', 'EMAIL_PORT', 'EMAIL_USER', 'EMAIL_PASSWORD'
    ]
    
    optional_vars = [
        'PORT', 'DB_POOL_SIZE', 'DB_MAX_OVERFLOW', 'FLASK_ENV', 'EMAIL_FROM'
    ]
    
    env_status = {"required": {}, "optional": {}}
    
    logger.info("Required Environment Variables:")
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            # Hide sensitive info
            if any(secret in var.lower() for secret in ['password', 'key', 'secret']):
                display_val = "***SET***"
            else:
                display_val = value[:30] + "..." if len(value) > 30 else value
            logger.info(f"  ✅ {var}: {display_val}")
            env_status["required"][var] = True
        else:
            logger.error(f"  ❌ {var}: NOT SET")
            env_status["required"][var] = False
    
    logger.info("\nOptional Environment Variables:")
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            logger.info(f"  ✅ {var}: {value}")
            env_status["optional"][var] = value
        else:
            logger.info(f"  ⚠️  {var}: Using default")
            env_status["optional"][var] = None
    
    return env_status

def check_python_environment():
    """Check Python environment and paths"""
    log_section("PYTHON ENVIRONMENT CHECK")
    
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Python Executable: {sys.executable}")
    logger.info(f"Current Working Directory: {os.getcwd()}")
    logger.info(f"Script Directory: {os.path.dirname(os.path.abspath(__file__))}")
    
    logger.info("\nPython Path (first 5 entries):")
    for i, path in enumerate(sys.path[:5]):
        logger.info(f"  {i}: {path}")
    
    # Check critical directories
    critical_dirs = ['backend', 'frontend', 'frontend/build']
    logger.info("\nCritical Directories:")
    for dir_name in critical_dirs:
        if os.path.exists(dir_name):
            logger.info(f"  ✅ {dir_name}: EXISTS")
        else:
            logger.error(f"  ❌ {dir_name}: MISSING")

def check_file_imports():
    """Check if key files can be imported"""
    log_section("IMPORT CHECK")
    
    # Add paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    sys.path.insert(0, os.path.join(current_dir, 'backend'))
    
    import_results = {}
    
    # Test basic imports
    basic_imports = ['flask', 'sqlalchemy', 'psycopg2', 'pdfkit']
    logger.info("Basic Package Imports:")
    for package in basic_imports:
        try:
            __import__(package)
            logger.info(f"  ✅ {package}: OK")
            import_results[package] = True
        except ImportError as e:
            logger.error(f"  ❌ {package}: FAILED - {e}")
            import_results[package] = False
    
    # Test application import
    logger.info("\nApplication Import:")
    try:
        from backend.minimal_app import app
        logger.info("  ✅ backend.minimal_app: OK")
        logger.info(f"  App name: {app.name}")
        logger.info(f"  App config keys: {list(app.config.keys())[:5]}...")
        import_results['backend_app'] = True
    except Exception as e:
        logger.error(f"  ❌ backend.minimal_app: FAILED - {e}")
        import traceback
        traceback.print_exc()
        import_results['backend_app'] = False
    
    return import_results

def check_database_connectivity():
    """Check database connection"""
    log_section("DATABASE CONNECTIVITY CHECK")
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL not set - skipping connectivity test")
        return False
    
    try:
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        
        logger.info(f"Database Host: {parsed.hostname}")
        logger.info(f"Database Port: {parsed.port}")
        logger.info(f"Database Name: {parsed.path[1:] if parsed.path else 'N/A'}")
        logger.info(f"Database User: {parsed.username}")
        logger.info(f"SSL Mode: {'Required' if 'sslmode=require' in database_url else 'Not specified'}")
        
        # Test connection
        import psycopg2
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logger.info(f"✅ Database Connection: SUCCESS")
        logger.info(f"PostgreSQL Version: {version[0][:50]}...")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Database Connection: FAILED - {e}")
        return False

def check_port_binding():
    """Check if port is available"""
    log_section("PORT BINDING CHECK")
    
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Target Port: {port}")
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            logger.warning(f"⚠️  Port {port} appears to be in use")
        else:
            logger.info(f"✅ Port {port} appears to be available")
        
        return True
    except Exception as e:
        logger.error(f"❌ Port check failed: {e}")
        return False

def run_comprehensive_diagnosis():
    """Run all diagnostic checks"""
    start_time = datetime.now()
    
    logger.info("🚀 DIGITAL OCEAN STARTUP DIAGNOSTICS")
    logger.info(f"Timestamp: {start_time}")
    logger.info(f"Platform: {sys.platform}")
    
    results = {
        "timestamp": start_time.isoformat(),
        "platform": sys.platform,
        "diagnostics": {}
    }
    
    # Run all checks
    try:
        results["diagnostics"]["environment"] = check_environment()
        check_python_environment()
        results["diagnostics"]["imports"] = check_file_imports()
        results["diagnostics"]["database"] = check_database_connectivity()
        results["diagnostics"]["port"] = check_port_binding()
        
    except Exception as e:
        logger.error(f"Diagnostic error: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    log_section("DIAGNOSTIC SUMMARY")
    
    env_ok = all(results["diagnostics"]["environment"]["required"].values())
    imports_ok = results["diagnostics"]["imports"].get("backend_app", False)
    db_ok = results["diagnostics"]["database"]
    
    if env_ok and imports_ok and db_ok:
        logger.info("🎉 ALL CRITICAL CHECKS PASSED - App should start successfully")
        results["overall_status"] = "SUCCESS"
    else:
        logger.error("❌ SOME CRITICAL CHECKS FAILED:")
        if not env_ok:
            logger.error("  - Environment variables missing")
        if not imports_ok:
            logger.error("  - Application import failed")
        if not db_ok:
            logger.error("  - Database connectivity failed")
        results["overall_status"] = "FAILURE"
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"Diagnostic completed in {duration:.2f} seconds")
    
    return results

if __name__ == "__main__":
    # Run diagnostics
    diagnostic_results = run_comprehensive_diagnosis()
    
    # Save results to file for debugging
    try:
        with open('/tmp/startup_diagnostic.json', 'w') as f:
            json.dump(diagnostic_results, f, indent=2, default=str)
        logger.info("Diagnostic results saved to /tmp/startup_diagnostic.json")
    except:
        pass  # Don't fail if we can't write file
    
    # Exit with appropriate code
    if diagnostic_results["overall_status"] == "SUCCESS":
        sys.exit(0)
    else:
        sys.exit(1)
