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

# Try to import the main app, but fall back to a minimal app if there are issues
try:
    logger.info("Attempting to import main application...")
    # Import Flask app from the backend/app.py file
    from backend.app import app as application
    logger.info("Main application imported successfully.")
    
    # Alias the application as 'app' for Gunicorn
    app = application
    
except Exception as e:
    logger.error(f"Error importing main application: {str(e)}")
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
                "error": str(e)
            })
        
        logger.info("Emergency minimal application created.")

# Direct execution (for local testing)
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
