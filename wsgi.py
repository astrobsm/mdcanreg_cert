#!/usr/bin/env python3
"""
WSGI Entry Point for DigitalOcean App Platform
Simplified and robust entry point for production deployment
"""
import os
import sys
import logging

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Set Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(app_dir, 'backend')

for path in [app_dir, backend_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

logger.info(f"🚀 Starting MDCAN BDM 2025 Application")
logger.info(f"📁 App directory: {app_dir}")
logger.info(f"🐍 Python version: {sys.version}")

# Environment check
env_vars = {
    'PORT': os.environ.get('PORT', 'not set'),
    'DATABASE_URL': 'configured' if os.environ.get('DATABASE_URL') else 'NOT SET',
    'ADMIN_PASSWORD': 'configured' if os.environ.get('ADMIN_PASSWORD') else 'NOT SET',
    'EMAIL_HOST': os.environ.get('EMAIL_HOST', 'not set')
}

for key, value in env_vars.items():
    logger.info(f"🔧 {key}: {value}")

try:
    # Import the Flask application
    logger.info("📦 Importing backend.minimal_app...")
    from backend.minimal_app import app
    
    logger.info("✅ Application imported successfully")
    logger.info(f"📋 App name: {app.name}")
    
    # Test basic app functionality
    with app.app_context():
        logger.info("🧪 Testing application context...")
        logger.info("✅ Application context is working")
    
    # Export for gunicorn
    application = app
    
except Exception as e:
    logger.error(f"❌ Failed to import application: {e}")
    import traceback
    traceback.print_exc()
    
    # Create a minimal error application
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    @app.route('/health')
    def error_response():
        return jsonify({
            "status": "error",
            "message": f"Application failed to start: {str(e)}",
            "app_dir": app_dir,
            "python_path": sys.path[:3]
        }), 500
    
    application = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🌐 Starting development server on 0.0.0.0:{port}")
    application.run(host='0.0.0.0', port=port, debug=False)

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
