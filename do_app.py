"""
Digital Ocean App Platform specific entry point
This provides a simplified way to run the app on Digital Ocean
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Get port from environment variable (Digital Ocean sets this)
try:
    port_str = os.environ.get('PORT')
    if port_str is None:
        logging.info("PORT environment variable not found, defaulting to 8080")
        port = 8080
    else:
        logging.info(f"Found PORT environment variable: '{port_str}'")
        port = int(port_str)
        logging.info(f"Successfully parsed PORT to integer: {port}")
except ValueError as e:
    logging.error(f"Error parsing PORT value: '{port_str}': {str(e)}")
    logging.info("Defaulting to port 8080")
    port = 8080

# Import the Flask app after setting up logging and port
try:
    from backend.minimal_app import app
    logging.info("Successfully imported app from backend.minimal_app")
except ImportError as e:
    logging.error(f"Error importing app: {str(e)}")
    from fallback_app import app
    logging.info("Imported fallback app instead")

# Export app for gunicorn to use
# The 'app' variable is what gunicorn will import

if __name__ == "__main__":
    logging.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
