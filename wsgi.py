"""
WSGI entry point for Gunicorn to run the Flask application.
This file allows Gunicorn to properly import the Flask app.
"""

from backend.app import app

# This allows Gunicorn to find and run our Flask app
if __name__ == "__main__":
    app.run()
