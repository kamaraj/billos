import os
import sys

# Add backend directory to path to resolve 'app' module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
