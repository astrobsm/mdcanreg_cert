#!/usr/bin/env python3
"""
CRITICAL: Production Gunicorn Configuration for Digital Ocean
Explicit configuration to resolve binding and deployment issues
"""

import os
import sys

# CRITICAL: Explicit binding configuration for Digital Ocean
bind = "0.0.0.0:8080"  # Hardcoded for reliability
workers = 1  # Single worker for 4GB instance
worker_class = "sync"
worker_connections = 1000

# CRITICAL: Timeout and lifecycle settings
timeout = 120  # Increased for PDF generation
keepalive = 2
max_requests = 500  # Restart workers after 500 requests
max_requests_jitter = 50
graceful_timeout = 30

# CRITICAL: Memory and resource management
worker_tmp_dir = "/dev/shm"  # Use memory for temporary files
max_requests_jitter = 50
preload_app = True  # Preload for better memory usage

# CRITICAL: Logging configuration for Digital Ocean visibility
loglevel = "info"
accesslog = "-"  # Log to stdout for Digital Ocean
errorlog = "-"   # Log to stderr for Digital Ocean
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
capture_output = True

# CRITICAL: Process naming for identification
proc_name = "mdcan_bdm_2025_platform"

# CRITICAL: Startup verification hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("🚀 MDCAN BDM 2025 - Gunicorn Starting")
    server.log.info(f"   Binding: {bind}")
    server.log.info(f"   Workers: {workers}")
    server.log.info(f"   Worker Class: {worker_class}")
    server.log.info(f"   Timeout: {timeout}s")
    server.log.info(f"   Python Version: {sys.version}")
    server.log.info(f"   Working Directory: {os.getcwd()}")
    server.log.info(f"   PORT Environment: {os.environ.get('PORT', 'not set')}")
    server.log.info(f"   DATABASE_URL: {'configured' if os.environ.get('DATABASE_URL') else 'not configured'}")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("♻️  Reloading workers due to configuration change")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info(f"Worker {worker.pid} received termination signal")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("✅ MDCAN BDM 2025 - Server ready to accept connections")
    server.log.info(f"   Listening on: {bind}")
    server.log.info(f"   Health check: http://localhost:8080/health")

def on_exit(server):
    """Called just before exiting."""
    server.log.info("👋 MDCAN BDM 2025 - Gunicorn server shutting down")

# CRITICAL: Environment variables for workers
raw_env = [
    "PYTHONPATH=/app:/app/backend",
    "PYTHONUNBUFFERED=1",
    "FLASK_ENV=production"
]

# CRITICAL: Security and performance settings
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Print critical configuration for debugging
print(f"🔧 CRITICAL GUNICORN CONFIGURATION:")
print(f"   Bind: {bind}")
print(f"   Workers: {workers}")
print(f"   Worker Class: {worker_class}")
print(f"   Timeout: {timeout}s")
print(f"   Preload App: {preload_app}")
print(f"   Log Level: {loglevel}")
print(f"   Process Name: {proc_name}")
print(f"✅ Configuration loaded successfully")
