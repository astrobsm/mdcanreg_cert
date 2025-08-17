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
    logging.info("✅ Application loaded successfully")
    
except Exception as e:
    logging.error(f"❌ Failed to load application: {e}")
    # Create minimal fallback app
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def health():
        return jsonify({"status": "error", "message": "Application failed to load"}), 500

# Export for gunicorn
application = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
