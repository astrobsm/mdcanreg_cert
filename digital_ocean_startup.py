"""
This script provides a direct way to start the application in Digital Ocean App Platform
It handles port binding in the simplest possible way
"""
import os
import sys
from flask import Flask, jsonify

# Create a minimal Flask app that will always work
app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "MDCAN BDM 2025 Certificate Platform - Startup",
        "info": "This is a fallback app for Digital Ocean deployment"
    })

if __name__ == "__main__":
    # Simple - use port 8080 for Digital Ocean
    print("Starting application on port 8080")
    app.run(host='0.0.0.0', port=8080)
