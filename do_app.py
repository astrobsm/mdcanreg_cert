"""
Digital Ocean App Platform specific entry point
This provides a simplified way to run the app on Digital Ocean
"""
import os
from backend.minimal_app import app

if __name__ == "__main__":
    # Get port from environment variable (Digital Ocean sets this)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
