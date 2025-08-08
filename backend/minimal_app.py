"""
Minimal version of the backend app that doesn't depend on pandas/numpy.
This can be used as a fallback if there are compatibility issues.
"""
from flask import Flask, jsonify, request, render_template_string, send_from_directory
from flask_cors import CORS
import os
import json
import sys

app = Flask(__name__)
CORS(app)

# Configure static folder
if os.path.exists('frontend/build'):
    static_folder = 'frontend/build'
elif os.path.exists('../frontend/build'):
    static_folder = '../frontend/build'
else:
    # Fallback to backend/static if frontend build doesn't exist
    static_folder = 'static' if os.path.exists('static') else None

# Serve React frontend from build folder
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve the React frontend"""
    if not path or path == '/':
        if static_folder and os.path.exists(os.path.join(static_folder, 'index.html')):
            return send_from_directory(static_folder, 'index.html')
        return jsonify({
            "status": "ok",
            "message": "MDCAN BDM 2025 Certificate Platform - Minimal Backend",
            "frontend": "Not available in minimal mode",
            "environment": {
                "DATABASE_URL": bool(os.environ.get('DATABASE_URL')),
                "EMAIL_HOST": bool(os.environ.get('EMAIL_HOST'))
            }
        })
    
    if static_folder and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    
    # For API routes, let them fall through to other handlers
    if path.startswith('api/'):
        return None
    
    # Return 404 for other paths
    return jsonify({"error": "Path not found"}), 404

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

@app.route('/api/test')
def test():
    """Test endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Backend API is working",
        "version": "minimal"
    })

@app.route('/api/status')
def status():
    """System status endpoint"""
    return jsonify({
        "status": "ok",
        "version": "minimal",
        "environment": {
            "python_version": sys.version,
            "flask_version": getattr(Flask, '__version__', 'unknown'),
            "database_connected": bool(os.environ.get('DATABASE_URL')),
            "email_configured": bool(os.environ.get('EMAIL_HOST')),
            "static_folder": static_folder
        },
        "system": {
            "platform": sys.platform,
            "cwd": os.getcwd(),
            "path": sys.path
        }
    })

# Only for direct execution
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
