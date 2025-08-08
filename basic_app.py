"""
Ultra-simple Digital Ocean app for deployment testing
"""
import os
from flask import Flask, jsonify

# Create the simplest possible app
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "MDCAN deployment test"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# The port must be exactly 8080 for Digital Ocean App Platform
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
