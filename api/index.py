import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = str(Path(__file__).parent.parent / "src")
sys.path.insert(0, src_path)

# Import the Dash app
from app import app

# Get the Flask server
server = app.server

# Export the app for Vercel
app = server