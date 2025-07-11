import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = str(Path(__file__).parent.parent / "src")
sys.path.insert(0, src_path)

# Import the Dash app
from app import app

# Create the serverless handler
server = app.server

# This is the Vercel serverless function handler
def handler(request, response):
    return server(request, response)