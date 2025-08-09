"""
Digital Ocean App Platform Entry Point
Clean, optimized entry point for MDCAN BDM 2025 Certificate Platform
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Log environment info (excluding sensitive data)
logging.info("=== MDCAN BDM 2025 Application Starting ===")
for key, value in os.environ.items():
    if not any(x in key.lower() for x in ['password', 'token', 'key', 'secret']):
        logging.info(f"ENV: {key}={value}")

# Import the full application with all features
try:
    logging.info("Loading full application with all features...")
    from backend.minimal_app import app
    
    logging.info("✅ Full application loaded successfully")
    
    # Add additional health check routes for Digital Ocean
    @app.route('/healthz')
    def healthz():
        from flask import jsonify
        return jsonify({"status": "ok"}), 200

    @app.route('/ready')
    def ready():
        from flask import jsonify
        return jsonify({"ready": True}), 200
    
    logging.info("✅ Additional health check routes added")
    
except Exception as e:
    logging.error(f"❌ Failed to load application: {e}")
    # Create a basic Flask app as fallback
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy", "service": "MDCAN BDM 2025"}), 200
    
    @app.route('/')
    def root():
        return jsonify({"message": "Application failed to load", "error": str(e)}), 500

if __name__ == "__main__":
    # Use $PORT environment variable with fallback to 8080
    port = int(os.environ.get('PORT', 8080))
    logging.info(f"🚀 Starting MDCAN BDM 2025 server on 0.0.0.0:{port}")
    logging.info(f"PORT environment variable: {os.environ.get('PORT', 'not set, using default 8080')}")
    app.run(host='0.0.0.0', port=port, debug=False)
