#!/usr/bin/env python3
"""
Entry point for the Chronoverse web application
"""
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = Config.PORT
    debug = os.environ.get('FLASK_ENV') != 'production'
    print(f"Starting Chronoverse on http://localhost:{port}")
    print(f"Press Ctrl+C to stop the server")
    app.run(debug=debug, host='0.0.0.0', port=port)

