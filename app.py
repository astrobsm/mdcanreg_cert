"""
Simplified entry point for the MDCAN BDM 2025 Certificate Platform.
This file helps with Digital Ocean deployment by ensuring the app module is correctly loaded.
"""
import os

# Import Flask app from the backend/app.py file
from backend.app import app as application

# Alias the application as 'app' for Gunicorn
app = application

# Direct execution (for local testing)
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
