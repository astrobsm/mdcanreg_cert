# Gunicorn configuration for Digital Ocean App Platform
bind = "0.0.0.0:8080"
workers = 1
worker_class = "sync"
timeout = 120
keepalive = 2
max_requests = 1000
preload_app = True
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Print configuration for debugging
print(f"Gunicorn starting on {bind}")
print(f"PORT environment variable: {os.environ.get('PORT', 'not set, using default 8080')}")
