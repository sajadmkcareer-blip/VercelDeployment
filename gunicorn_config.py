"""
Gunicorn Configuration File
Gunicorn is a Python WSGI HTTP Server for production use.

This configuration file is used when running the application with gunicorn.
Gunicorn is better suited for production than Flask's development server.
"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
backlog = 2048

# Worker processes
# For Render.com free tier (512MB RAM), use 2 workers to avoid memory issues
# For paid tiers, you can use more workers
# Formula for paid tiers: (2 x CPU cores) + 1
if os.environ.get('RENDER') or os.environ.get('RENDER_INSTANCE_ID'):
    # Running on Render - use fewer workers for free tier
    workers = 2
else:
    # Local development or other platforms
    workers = multiprocessing.cpu_count() * 2 + 1

# Worker class
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "forex-trading-signals-api"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed in future)
# keyfile = None
# certfile = None

