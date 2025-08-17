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

try:
    # Import the main application
    logging.info("Loading MDCAN BDM 2025 Application...")
    from backend.minimal_app import app
    
    # Add basic health check for deployment verification
    @app.route('/deploy-health')
    def deploy_health():
        from flask import jsonify
        import os
        return jsonify({
            "status": "ok",
            "message": "MDCAN BDM 2025 Application loaded successfully",
            "database_url_configured": bool(os.environ.get('DATABASE_URL')),
            "port": os.environ.get('PORT', '8080'),
            "environment": os.environ.get('FLASK_ENV', 'development')
        })
    
    logging.info("✅ Application loaded successfully")
    
except Exception as e:
    logging.error(f"❌ Failed to load application: {e}")
    # Create minimal fallback app
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    @app.route('/health')
    def health():
        return jsonify({"status": "error", "message": "Application failed to load"}), 500

# Export for gunicorn
application = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    logging.info(f"Starting application on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)
