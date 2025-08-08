"""
Digital Ocean App Platform Entry Point
A simplified script designed specifically for Digital Ocean App Platform deployment
"""
import os
import sys
import logging
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Create a simple Flask app that will work on Digital Ocean
app = Flask(__name__, static_folder='./frontend/build/static', static_url_path='/static')

# Health check endpoint - critical for Digital Ocean health checks
@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# Root endpoint
@app.route('/')
def root():
    return jsonify({
        "status": "ok", 
        "message": "MDCAN BDM 2025 Certificate Platform", 
        "info": "Digital Ocean simplified deployment"
    })

# Log environment variables for debugging
logging.info("=== Environment Variables (excluding sensitive data) ===")
for key, value in os.environ.items():
    if not any(x in key.lower() for x in ['password', 'token', 'key', 'secret']):
        logging.info(f"{key}: {value}")

# Import the actual application only after setting up the basic endpoints
try:
    logging.info("Attempting to import the full application...")
    from backend.minimal_app import app as full_app
    
    # Replace our simple app with the full application
    app = full_app
    logging.info("Successfully imported full application")
except Exception as e:
    logging.error(f"Error importing full application: {e}")
    logging.info("Continuing with simplified app for health checks")

if __name__ == "__main__":
    # Get port - hardcoded to 8080 for Digital Ocean
    port = 8080
    logging.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
