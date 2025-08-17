"""
Entry point for MDCAN BDM 2025 Certificate Platform
Compatible with both app:app and wsgi:application deployment patterns
Provides fallback if wsgi.py has issues
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'backend'))

logger.info(f"Loading MDCAN app from {current_dir}")

try:
    # Try importing from backend first
    from backend.minimal_app import app
    logger.info("✅ Successfully imported from backend.minimal_app")
    
    @app.route('/app-health')
    def app_health():
        return {"status": "ok", "message": "App.py entry point working", "source": "backend.minimal_app"}
    
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    # Fallback to create minimal app
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    @app.route('/health')
    @app.route('/app-health')
    def fallback_health():
        return jsonify({
            "status": "error",
            "message": "Backend import failed, using fallback",
            "error": str(e),
            "working_dir": os.getcwd(),
            "python_path": sys.path[:3]
        }), 500

except Exception as e:
    logger.error(f"❌ Unexpected error: {e}")
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    @app.route('/health')
    @app.route('/app-health')
    def error_health():
        return jsonify({
            "status": "error", 
            "message": "App load failed",
            "error": str(e)
        }), 500

# Export for gunicorn (alternative to wsgi.py)
application = app

if __name__ == "__main__":
    # Use $PORT environment variable with fallback to 8080
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🚀 Starting MDCAN BDM 2025 server on 0.0.0.0:{port}")
    logger.info(f"PORT environment variable: {os.environ.get('PORT', 'not set, using default 8080')}")
    app.run(host='0.0.0.0', port=port, debug=False)
