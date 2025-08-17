#!/usr/bin/env python3
"""
Startup Verification Script for MDCAN BDM 2025 Platform
Helps diagnose deployment issues
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_environment():
    """Verify critical environment variables and dependencies"""
    logger.info("🔍 Starting Environment Verification")
    
    # Check Python version
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path[:3]}...")
    
    # Check critical environment variables
    port = os.environ.get('PORT', 'NOT SET')
    logger.info(f"PORT: {port}")
    
    database_url = os.environ.get('DATABASE_URL', 'NOT SET')
    if database_url != 'NOT SET':
        # Sanitize database URL for logging
        if '@' in database_url:
            sanitized = database_url.split('@')[0] + '@***'
        else:
            sanitized = database_url[:20] + '...' if len(database_url) > 20 else database_url
        logger.info(f"DATABASE_URL: {sanitized}")
    else:
        logger.warning("DATABASE_URL: NOT SET")
    
    # Check email configuration
    email_host = os.environ.get('EMAIL_HOST', 'NOT SET')
    email_user = os.environ.get('EMAIL_USER', 'NOT SET')
    logger.info(f"EMAIL_HOST: {email_host}")
    logger.info(f"EMAIL_USER: {email_user}")
    
    # Check file system
    try:
        logger.info(f"Current directory contents: {os.listdir('.')[:10]}...")
    except Exception as e:
        logger.error(f"Error listing directory: {e}")
    
    # Check if backend directory exists
    backend_exists = os.path.exists('backend')
    logger.info(f"Backend directory exists: {backend_exists}")
    
    if backend_exists:
        try:
            backend_files = os.listdir('backend')[:5]
            logger.info(f"Backend files: {backend_files}...")
        except Exception as e:
            logger.error(f"Error listing backend directory: {e}")
    
    # Check frontend build
    frontend_build_exists = os.path.exists('frontend/build')
    logger.info(f"Frontend build exists: {frontend_build_exists}")
    
    if frontend_build_exists:
        try:
            build_files = os.listdir('frontend/build')[:5]
            logger.info(f"Frontend build files: {build_files}...")
        except Exception as e:
            logger.error(f"Error listing frontend build: {e}")
    
    # Try importing Flask
    try:
        from flask import Flask
        logger.info("✅ Flask import successful")
    except ImportError as e:
        logger.error(f"❌ Flask import failed: {e}")
    
    # Try importing the app
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
        from minimal_app import app
        logger.info("✅ App import successful")
        
        # Test basic app functionality
        with app.test_client() as client:
            response = client.get('/health')
            logger.info(f"Health check status: {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ App import/test failed: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("🏁 Environment Verification Complete")

if __name__ == "__main__":
    verify_environment()
