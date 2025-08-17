#!/usr/bin/env python3
"""
Digital Ocean Pre-startup Verification
Run this script to verify deployment readiness
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("🔍 MDCAN BDM 2025 - Pre-startup verification")
    
    # Test 1: Environment variables
    logger.info("Testing environment variables...")
    required_vars = ['DATABASE_URL', 'SECRET_KEY', 'ADMIN_PASSWORD']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        return False
    else:
        logger.info("✅ All required environment variables present")
    
    # Test 2: Python imports
    logger.info("Testing Python imports...")
    try:
        # Add paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        sys.path.insert(0, os.path.join(current_dir, 'backend'))
        
        import flask
        import sqlalchemy
        import psycopg2
        from backend.minimal_app import app
        logger.info("✅ All imports successful")
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return False
    
    # Test 3: Database connection
    logger.info("Testing database connection...")
    try:
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            import psycopg2
            conn = psycopg2.connect(database_url)
            conn.close()
            logger.info("✅ Database connection successful")
        else:
            logger.warning("⚠️  DATABASE_URL not set, skipping database test")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
    
    # Test 4: Application creation
    logger.info("Testing application startup...")
    try:
        with app.app_context():
            logger.info(f"✅ Application context working: {app.name}")
    except Exception as e:
        logger.error(f"❌ Application context failed: {e}")
        return False
    
    logger.info("🎉 All pre-startup checks passed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
