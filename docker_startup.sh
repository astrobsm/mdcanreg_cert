#!/bin/bash
# This script handles the PORT environment variable correctly
# It's used as the entry point for the Docker container

# Get the PORT environment variable, default to 8080 if not set
PORT=${PORT:-8080}

echo "Starting server on port $PORT"

# Run gunicorn with the port from the environment
exec gunicorn --bind "0.0.0.0:$PORT" --workers 1 --timeout 120 --log-level debug --capture-output --enable-stdio-inheritance do_app:app
