"""
Digital Ocean App Platform specific entry point
This provides a simplified way to run the app on Digital Ocean
"""
import os
import logging
from backend.minimal_app import app

# Get port from environment variable (Digital Ocean sets this)
# Use a try-except block to handle potential conversion errors
try:
    port_str = os.environ.get('PORT', '8080')
    port = int(port_str)
    logging.info(f"Using port {port} from environment variable")
except ValueError:
    logging.warning(f"Invalid PORT value: '{port_str}', defaulting to 8080")
    port = 8080

# Export app for gunicorn to use
# The 'app' variable is what gunicorn will import

if __name__ == "__main__":
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
