"""
Vercel Serverless Function Entry Point
This file is the entry point for Vercel deployment.
It imports and runs the Flask application.

For Vercel Python deployment, we need to expose the Flask app directly.
Vercel's @vercel/python builder automatically handles WSGI applications.
"""
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app
from app import app

# Vercel expects the app to be available as a WSGI application
# The @vercel/python builder will automatically handle this
# For Vercel, we just need to expose the app object
# No handler function needed - Vercel handles WSGI apps directly


