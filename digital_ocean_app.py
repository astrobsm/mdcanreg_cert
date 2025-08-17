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
logging.info("Version: 2.0 with /api/register endpoint and database initialization")
for key, value in os.environ.items():
    if not any(x in key.lower() for x in ['password', 'token', 'key', 'secret']):
        logging.info(f"ENV: {key}={value}")

# Import the full application with all features
try:
    logging.info("Loading full application with WhatsApp integration...")
    logging.info("Python path: %s", sys.path)
    logging.info("Current working directory: %s", os.getcwd())
    logging.info("Backend directory exists: %s", os.path.exists('backend'))
    logging.info("Backend minimal_app.py exists: %s", os.path.exists('backend/minimal_app.py'))
    
    # Ensure backend is in Python path
    backend_path = os.path.join(os.getcwd(), 'backend')
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    # Import from backend directory where minimal_app.py is located
    from backend.minimal_app import app
    
    logging.info("✅ Full application loaded successfully")
    logging.info("App routes available: %s", [rule.rule for rule in app.url_map.iter_rules()])
    
    # Add additional health check routes for Digital Ocean
    @app.route('/healthz')
    def healthz():
        from flask import jsonify
        return jsonify({"status": "ok", "app": "mdcan-bdm-2025"}), 200

    @app.route('/ready')
    def ready():
        from flask import jsonify
        return jsonify({"ready": True, "version": "production"}), 200
    
    logging.info("✅ Additional health check routes added")
    
except Exception as e:
    logging.error(f"❌ Failed to load application: {e}")
    logging.error(f"❌ Exception type: {type(e).__name__}")
    import traceback
    logging.error(f"❌ Full traceback: {traceback.format_exc()}")
    
    # Create a basic Flask app as fallback
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy", "service": "MDCAN BDM 2025"}), 200
    
    @app.route('/')
    def root():
        return jsonify({
            "message": "Application failed to load", 
            "error": str(e),
            "error_type": type(e).__name__,
            "note": "Check application logs for full traceback"
        }), 500
    
    @app.route('/debug')
    def debug():
        import traceback
        return jsonify({
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }), 500

if __name__ == "__main__":
    # Use $PORT environment variable with fallback to 8080
    port = int(os.environ.get('PORT', 8080))
    logging.info(f"🚀 Starting MDCAN BDM 2025 server on 0.0.0.0:{port}")
    logging.info(f"PORT environment variable: {os.environ.get('PORT', 'not set, using default 8080')}")
    app.run(host='0.0.0.0', port=port, debug=False)
