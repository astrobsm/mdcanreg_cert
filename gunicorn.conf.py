#!/usr/bin/env python3
"""
Production Gunicorn Configuration for Digital Ocean
Optimized for Digital Ocean App Platform deployment
"""

import os
import sys

# Basic server configuration
bind = f"0.0.0.0:{os.environ.get('PORT', 8080)}"
workers = 1  # Single worker for 4GB instance
worker_class = "sync"
worker_connections = 1000

# Timeout settings for Digital Ocean
timeout = 120  # Increased for PDF generation
keepalive = 2
max_requests = 500  # Restart workers after 500 requests
max_requests_jitter = 50

# Memory management
try:
    import resource
    # Set memory limit to 3GB per worker
    def worker_memory_limit():
        resource.setrlimit(resource.RLIMIT_AS, (3000 * 1024 * 1024, 3000 * 1024 * 1024))
except ImportError:
    pass

# Logging configuration
loglevel = os.environ.get('LOG_LEVEL', 'info')
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'mdcan_bdm_2025'

# Startup hooks for debugging
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("🚀 MDCAN BDM 2025 - Starting Gunicorn server")
    server.log.info(f"Python version: {sys.version}")
    server.log.info(f"Working directory: {os.getcwd()}")
    server.log.info(f"PORT: {os.environ.get('PORT', 'not set')}")
    server.log.info(f"DATABASE_URL: {'configured' if os.environ.get('DATABASE_URL') else 'not configured'}")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("♻️  Reloading workers")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info(f"Worker {worker.pid} received INT or QUIT signal")

def on_exit(server):
    """Called just before exiting."""
    server.log.info("👋 MDCAN BDM 2025 - Gunicorn server shutting down")

# Preload application for better memory usage
preload_app = True

# Environment variables to pass to workers
raw_env = [
    f"PYTHONPATH=/app:/app/backend",
    f"PYTHONUNBUFFERED=1"
]

# Print configuration for debugging
print(f"🔧 Gunicorn configuration loaded")
print(f"   Bind: {bind}")
print(f"   Workers: {workers}")
print(f"   PORT env: {os.environ.get('PORT', 'not set, using default 8080')}")
print(f"   Working dir: {os.getcwd()}")
print(f"   Python path: {sys.path[:2]}...")
