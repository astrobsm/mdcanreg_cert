"""
Minimal version of the backend app that doesn't depend on pandas/numpy.
This can be used as a fallback if there are compatibility issues.
"""
from flask import Flask, jsonify, request
import os

app = Flask(__name__)

@app.route('/')
def home():
    """Homepage route"""
    return jsonify({
        "status": "ok",
        "message": "MDCAN BDM 2025 Certificate Platform - Minimal Backend",
        "environment": {
            "DATABASE_URL": bool(os.environ.get('DATABASE_URL')),
            "EMAIL_HOST": bool(os.environ.get('EMAIL_HOST'))
        }
    })

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

# Only for direct execution
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
