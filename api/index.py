"""
Vercel Serverless Function Entry Point for BillOS API.

This module serves as the entry point for the Vercel Python runtime.
It imports the FastAPI app and exports it as 'app' for Vercel's ASGI handler.
"""
import sys
import os

# Add the backend directory to the path BEFORE any imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_dir = os.path.join(project_root, 'backend')

# Insert at the beginning of sys.path
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Set VERCEL environment variable before importing app
os.environ["VERCEL"] = "1"

# Import the FastAPI app - Vercel expects this to be named 'app'
from app.main import app

# Export app for Vercel (this is the ASGI application)
# Vercel's @vercel/python runtime automatically detects ASGI apps
