"""
Vercel Serverless Function Entry Point for BillOS API.
This file handles all /api/* requests.
"""
import sys
import os

# Add the backend directory to the path so we can import the app
backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
sys.path.insert(0, backend_dir)

# Import the FastAPI app
from app.main import app

# Vercel expects a handler, but for FastAPI, we export the app directly
# The @vercel/python runtime will handle this
