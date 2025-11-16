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
# Formula: (2 x CPU cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1
# For Render.com free tier, use fewer workers to avoid memory issues
# Uncomment the line below if you're on free tier
# workers = 2

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

