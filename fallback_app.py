"""
Fallback minimal app for Digital Ocean deployment.
This provides a basic working app if the main app fails to load due to dependency issues.
"""
import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    """Return a simple health check response."""
    return jsonify({
        "status": "ok",
        "message": "MDCAN BDM 2025 Certificate Platform - Minimal Mode",
        "info": "Running in fallback mode due to dependency issues",
        "environment": {
            "DATABASE_URL": bool(os.environ.get('DATABASE_URL')),
            "EMAIL_CONFIG": bool(os.environ.get('EMAIL_HOST'))
        }
    })

@app.route('/health')
def health():
    """Simple health check endpoint."""
    return "ok"

# This will only run when this file is executed directly
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
