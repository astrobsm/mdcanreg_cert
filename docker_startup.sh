#!/bin/bash
# This script handles the PORT environment variable correctly
# It's used as the entry point for the Docker container

# More robust PORT handling
if [ -z "$PORT" ]; then
  echo "PORT environment variable not set, defaulting to 8080"
  PORT=8080
else
  echo "PORT environment variable is set to: $PORT"
  # Verify PORT is a number
  if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "WARNING: PORT is not a valid number: '$PORT', defaulting to 8080"
    PORT=8080
  fi
fi

echo "Starting server on port $PORT"

# Run gunicorn with the port from the environment
# Using explicit port number instead of variable substitution
exec gunicorn --bind "0.0.0.0:$PORT" --workers 1 --timeout 120 --log-level debug --capture-output --enable-stdio-inheritance --error-logfile=- --access-logfile=- do_app:app
