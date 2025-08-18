#!/usr/bin/env python3
"""
Optimized Gunicorn Configuration for DigitalOcean App Platform
"""

import os

# Dynamic binding for DigitalOcean
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"

# Resource configuration optimized for apps-s-2vcpu-4gb
workers = 2
worker_class = "sync"
timeout = 30
keepalive = 2
max_requests = 500
max_requests_jitter = 50

# Logging for DigitalOcean
loglevel = "info"
accesslog = "-"
errorlog = "-"
capture_output = True

# Basic preload for faster startup
preload_app = True
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
capture_output = True

# CRITICAL: Process naming for identification
proc_name = "mdcan_bdm_2025_platform"

# CRITICAL: Security and performance settings
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
forwarded_allow_ips = "*"  # Allow all for Digital Ocean load balancer

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
    logging.info(f"Python version: {sys.version}")
    logging.info(f"Working directory: {os.getcwd()}")

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
