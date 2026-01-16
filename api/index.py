"""
Vercel Serverless Function Entry Point for BillOS API.
Uses the Mangum adapter for ASGI compatibility.
"""
import sys
import os

# Add backend to path
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(root, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

os.environ["VERCEL"] = "1"

from app.main import app

# Vercel expects 'app' or 'handler' export for ASGI apps
