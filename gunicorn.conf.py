#!/usr/bin/env python3
"""
Optimized Gunicorn Configuration for DigitalOcean App Platform
"""

import os
import sys
import logging

# CRITICAL: Dynamic binding for DigitalOcean
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"

# Resource configuration optimized for apps-s-2vcpu-4gb
workers = 2
worker_class = "sync"
timeout = 120  # Increased for startup
keepalive = 2
max_requests = 500
max_requests_jitter = 50
graceful_timeout = 30

# Logging for DigitalOcean
loglevel = "info"
accesslog = "-"
errorlog = "-"
capture_output = True

# Performance settings
preload_app = True
worker_tmp_dir = "/dev/shm"

# Security settings
limit_request_line = 4096
limit_request_fields = 100
forwarded_allow_ips = "*"

# Process naming
proc_name = "mdcan_bdm_2025"

def on_starting(server):
    """Called just before the master process is initialized."""
    logging.info(f"🚀 MDCAN BDM 2025 - Gunicorn Starting")
    logging.info(f"   Binding to: {bind}")
    logging.info(f"   Workers: {workers}")
    logging.info(f"   Timeout: {timeout}s")
    logging.info(f"   Python: {sys.version.split()[0]}")

def post_worker_init(worker):
    """Called after a worker has initialized the application."""
    logging.info(f"✅ Worker {worker.pid} ready")

def on_exit(server):
    """Called when gunicorn is about to exit."""
    logging.info("👋 MDCAN BDM 2025 - Gunicorn Exiting")
