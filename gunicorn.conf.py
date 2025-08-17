# Gunicorn configuration for Digital Ocean App Platform
import os

# Use PORT environment variable from Digital Ocean
port = os.environ.get('PORT', '8080')
bind = f"0.0.0.0:{port}"

workers = 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
accesslog = "-"
errorlog = "-"
loglevel = "info"
capture_output = True
enable_stdio_inheritance = True

# Print configuration for debugging
print(f"Gunicorn starting on {bind}")
print(f"PORT environment variable: {os.environ.get('PORT', 'not set, using default 8080')}")
