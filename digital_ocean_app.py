"""
Digital Ocean App Platform Entry Point
Clean, optimized entry point for MDCAN BDM 2025 Certificate Platform
"""
import os
import sys
import logging
from flask import Flask, jsonify, send_from_directory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Create the primary Flask app
app = Flask(__name__, 
            static_folder='./frontend/build/static',
            static_url_path='/static')

# Health check endpoint - CRITICAL for Digital Ocean health checks
@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "MDCAN BDM 2025"}), 200

# Additional health check routes
@app.route('/healthz')
def healthz():
    return jsonify({"status": "ok"}), 200

@app.route('/ready')
def ready():
    return jsonify({"ready": True}), 200

# Root endpoint - serves as primary health check
@app.route('/')
def root():
    return jsonify({
        "status": "ok", 
        "message": "MDCAN BDM 2025 Certificate Platform", 
        "version": "1.0.0",
        "deployment": "Digital Ocean App Platform"
    }), 200

# Log environment info (excluding sensitive data)
logging.info("=== MDCAN BDM 2025 Application Starting ===")
for key, value in os.environ.items():
    if not any(x in key.lower() for x in ['password', 'token', 'key', 'secret']):
        logging.info(f"ENV: {key}={value}")

# Import and integrate the full application
try:
    logging.info("Loading full application features...")
    from backend.minimal_app import app as full_app
    
    # Copy all routes from the full app to our main app
    for rule in full_app.url_map.iter_rules():
        endpoint = full_app.view_functions[rule.endpoint]
        app.add_url_rule(rule.rule, rule.endpoint, endpoint, methods=rule.methods)
    
    # Copy configuration
    app.config.update(full_app.config)
    
    logging.info("✅ Full application features loaded successfully")
    
except Exception as e:
    logging.warning(f"⚠️  Could not load full application: {e}")
    logging.info("🔄 Running in basic mode with health checks only")

# Serve React frontend (for non-API routes)
@app.route('/app', defaults={'path': ''})
@app.route('/app/<path:path>')
def serve_frontend(path):
    """Serve React frontend files"""
    try:
        if path and not path.startswith('api'):
            frontend_path = os.path.join('./frontend/build', path)
            if os.path.exists(frontend_path):
                return send_from_directory('./frontend/build', path)
        return send_from_directory('./frontend/build', 'index.html')
    except Exception as e:
        logging.error(f"Frontend serving error: {e}")
        return jsonify({"error": "Frontend not available"}), 404

if __name__ == "__main__":
    # Use $PORT environment variable with fallback to 8080
    port = int(os.environ.get('PORT', 8080))
    logging.info(f"🚀 Starting MDCAN BDM 2025 server on 0.0.0.0:{port}")
    logging.info(f"PORT environment variable: {os.environ.get('PORT', 'not set, using default 8080')}")
    app.run(host='0.0.0.0', port=port, debug=False)
