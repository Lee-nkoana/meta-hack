
import sys
import os

# Add the 'backend' directory to sys.path so imports work
# Vercel places the project root in the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(os.path.dirname(current_dir), 'backend')
sys.path.append(backend_dir)

from app.main import app

# Vercel looks for a variable named 'app'
# This acts as the serverless function handler
