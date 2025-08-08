"""
Entry point for the MDCAN BDM 2025 Certificate Platform.
This file helps with Digital Ocean deployment by ensuring the app module is correctly loaded.
"""
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add current directory to path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    logger.info(f"Added {current_dir} to sys.path")

# Print current directory structure for debugging
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Directory contents: {os.listdir('.')}")
if os.path.exists('backend'):
    logger.info(f"Backend directory contents: {os.listdir('backend')}")
else:
    logger.info("Backend directory not found")

# Try to import the main app, but fall back to a minimal app if there are issues
try:
    logger.info("Attempting to import main application...")
    # Try multiple import paths to be more robust
    try:
        # Import Flask app from the backend/app.py file (standard path)
        from backend.app import app as application
        logger.info("Main application imported successfully from backend.app.")
    except ImportError as e:
        logger.warning(f"Failed to import from backend.app: {e}")
        # Try alternative import path
        sys.path.insert(0, os.path.join(current_dir, 'backend'))
        from app import app as application
        logger.info("Main application imported successfully from direct app import.")
    
    # Alias the application as 'app' for Gunicorn
    app = application
    
except Exception as e:
    logger.error(f"Error importing main application: {str(e)}")
    logger.error(f"Exception type: {type(e).__name__}")
    logger.error(f"Exception traceback: {sys.exc_info()}")
    logger.info("Falling back to minimal application...")
    
    # Import the fallback minimal app
    try:
        from fallback_app import app
        logger.info("Fallback application loaded successfully.")
    except Exception as fallback_error:
        logger.error(f"Error loading fallback app: {str(fallback_error)}")
        
        # If even the fallback app fails, create a super minimal app
        from flask import Flask, jsonify
        app = Flask(__name__)
        
        @app.route('/')
        def emergency_home():
            return jsonify({
                "status": "degraded",
                "message": "Emergency Fallback Mode",
                "error": str(e),
                "exception_type": str(type(e).__name__),
                "path_info": {
                    "cwd": os.getcwd(),
                    "sys_path": sys.path
                }
            })
        
        @app.route('/debug')
        def debug_info():
            """Return debug information to help diagnose deployment issues."""
            return jsonify({
                "status": "debug",
                "environment": dict(os.environ),
                "directory_structure": {
                    "root": os.listdir("."),
                    "backend_exists": os.path.exists("backend"),
                    "backend_contents": os.listdir("backend") if os.path.exists("backend") else "N/A"
                },
                "python_info": {
                    "version": sys.version,
                    "path": sys.path
                }
            })
        
        logger.info("Emergency minimal application created.")

# Direct execution (for local testing)
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
