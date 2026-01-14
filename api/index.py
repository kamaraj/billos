"""
Vercel Serverless Function Entry Point for BillOS API.
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add the backend directory to the path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_dir)

# Set VERCEL environment variable before importing app
os.environ["VERCEL"] = "1"

try:
    from app.main import app
    # For Vercel Python runtime with FastAPI
    handler = app
except Exception as e:
    # Fallback error handler if import fails
    class handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_msg = json.dumps({
                "error": "Failed to initialize API",
                "detail": str(e),
                "backend_dir": backend_dir,
                "sys_path": sys.path[:5]
            })
            self.wfile.write(error_msg.encode())
        
        def do_POST(self):
            self.do_GET()
