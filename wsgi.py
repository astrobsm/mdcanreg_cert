#!/usr/bin/env python3
"""
WSGI Entry Point for Digital Ocean App Platform
Simplified, robust entry point for production deployment
"""
import os
import sys
import logging

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Set Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

backend_dir = os.path.join(app_dir, 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Log startup information
logging.info(f"Starting MDCAN BDM 2025 Application from {app_dir}")
logging.info(f"Python path: {sys.path[:3]}...")  # Log first 3 entries

# Environment variables check
port = os.environ.get('PORT', 'not set')
database_url = os.environ.get('DATABASE_URL', 'not configured')
admin_password = os.environ.get('ADMIN_PASSWORD', 'not configured')
email_host = os.environ.get('EMAIL_HOST', 'not configured')

logging.info(f"Environment: PORT={port}")
logging.info(f"Database URL: {'configured' if database_url != 'not configured' else 'NOT CONFIGURED'}")
logging.info(f"Admin Password: {'configured' if admin_password != 'not configured' else 'NOT CONFIGURED'}")
logging.info(f"Email Host: {'configured' if email_host != 'not configured' else 'NOT CONFIGURED'}")

# Check for critical missing environment variables
missing_vars = []
if database_url == 'not configured':
    missing_vars.append('DATABASE_URL')
if admin_password == 'not configured':
    missing_vars.append('ADMIN_PASSWORD')

if missing_vars:
    logging.warning(f"⚠️ Missing critical environment variables: {', '.join(missing_vars)}")
else:
    logging.info("✅ All critical environment variables are configured")

try:
    # Import the main application
    logging.info("Loading backend.minimal_app...")
    from backend.minimal_app import app
    
    # Add comprehensive health check for deployment verification
    @app.route('/deploy-health')
    def deploy_health():
        from flask import jsonify
        import os
        return jsonify({
            "status": "ok",
            "message": "MDCAN BDM 2025 Application loaded successfully",
            "database_url_configured": bool(os.environ.get('DATABASE_URL')),
            "port": os.environ.get('PORT', '8080'),
            "environment": os.environ.get('FLASK_ENV', 'development'),
            "instance_resources": {
                "pool_size": os.environ.get('DB_POOL_SIZE', '3'),
                "max_overflow": os.environ.get('DB_MAX_OVERFLOW', '5')
            },
            "app_name": app.name,
            "python_path": app_dir
        })
    
    @app.route('/startup-status')
    def startup_status():
        from flask import jsonify
        return jsonify({
            "status": "success", 
            "message": "Application started successfully",
            "wsgi_loaded": True,
            "backend_imported": True
        })
    
    logging.info("✅ Application loaded successfully")
    
except ImportError as ie:
    logging.error(f"❌ Import error loading application: {ie}")
    # Create minimal fallback app with detailed error info
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    @app.route('/health')
    @app.route('/startup-status')
    def health():
        return jsonify({
            "status": "error", 
            "message": "Application import failed",
            "error": str(ie),
            "python_path": sys.path[:3],
            "working_dir": os.getcwd(),
            "app_dir": app_dir
        }), 500

except Exception as e:
    logging.error(f"❌ Unexpected error loading application: {e}")
    import traceback
    traceback.print_exc()
    # Create minimal fallback app
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    @app.route('/health')
    @app.route('/startup-status')
    def health():
        return jsonify({
            "status": "error", 
            "message": "Application failed to load",
            "error": str(e)
        }), 500

# Export for gunicorn
application = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    logging.info(f"Starting application on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)
