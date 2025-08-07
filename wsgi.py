"""
WSGI entry point for Gunicorn to run the Flask application.
This file allows Gunicorn to properly import the Flask app.
"""

import os
from flask import Flask, jsonify

# Check if we should run in health check mode (for initial deployment testing)
if os.environ.get('HEALTH_CHECK_MODE') == 'true':
    app = Flask(__name__)
    
    @app.route('/')
    def health_check():
        """Simple health check endpoint to verify the app is running."""
        return jsonify({
            "status": "ok",
            "message": "MDCAN BDM 2025 Certificate Platform is running in health check mode",
            "env_vars_configured": {
                "DATABASE_URL": bool(os.environ.get('DATABASE_URL')),
                "EMAIL_HOST": bool(os.environ.get('EMAIL_HOST')),
                "EMAIL_PORT": bool(os.environ.get('EMAIL_PORT')),
                "EMAIL_USER": bool(os.environ.get('EMAIL_USER')),
                "EMAIL_PASSWORD": bool(os.environ.get('EMAIL_PASSWORD', '')),
                "EMAIL_FROM": bool(os.environ.get('EMAIL_FROM'))
            }
        })
    
    @app.route('/ping')
    def ping():
        """Even simpler endpoint for minimal response time."""
        return "pong"
else:
    # Import the actual application
    from backend.app import app

# This allows Gunicorn to find and run our Flask app
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
