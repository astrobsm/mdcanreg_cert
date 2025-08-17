#!/usr/bin/env python3
"""
CRITICAL: Production Gunicorn Configuration for Digital Ocean
Explicit configuration to resolve binding and deployment issues
"""

import os
import sys

# CRITICAL: Dynamic binding configuration for Digital Ocean
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"  # Use dynamic PORT from environment
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
    import logging
    logging.info(f"🚀 MDCAN BDM 2025 Platform - Gunicorn Starting")
    logging.info(f"Binding to: {bind}")
    logging.info(f"Workers: {workers}")
    logging.info(f"Worker class: {worker_class}")
    logging.info(f"Timeout: {timeout}s")
    logging.info(f"Environment PORT: {os.environ.get('PORT', 'not set')}")

def on_reload(server):
    """Called when configuration is reloaded."""
    import logging
    logging.info("🔄 MDCAN BDM 2025 Platform - Gunicorn Reloading")

def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal."""
    import logging
    logging.info(f"⚠️ Worker {worker.pid} interrupted")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    import logging
    logging.info(f"🔧 Forking worker {worker}")

def post_fork(server, worker):
    """Called after a worker has been forked."""
    import logging
    logging.info(f"✅ Worker {worker.pid} forked successfully")

def post_worker_init(worker):
    """Called after a worker has initialized the application."""
    import logging
    logging.info(f"🎯 Worker {worker.pid} initialized and ready")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    import logging
    logging.error(f"💥 Worker {worker.pid} aborted")

def on_exit(server):
    """Called when gunicorn is about to exit."""
    import logging
    logging.info("👋 MDCAN BDM 2025 Platform - Gunicorn Exiting")
