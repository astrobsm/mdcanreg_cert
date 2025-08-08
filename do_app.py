"""
Digital Ocean App Platform specific entry point
This provides a simplified way to run the app on Digital Ocean
"""
import os
import sys
import logging

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Log all environment variables for debugging (except sensitive ones)
for key, value in sorted(os.environ.items()):
    if not any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key']):
        logging.info(f"Environment variable: {key}={value}")

# Set a fixed port for Digital Ocean - this is critical
# Digital Ocean App Platform requires the app to listen on port 8080
PORT = 8080
logging.info(f"Using fixed port {PORT} for Digital Ocean App Platform")

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
    logging.info(f"Starting server on port {PORT}")
    app.run(host='0.0.0.0', port=PORT)
