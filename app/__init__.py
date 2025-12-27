from flask import Flask
import os
import sys

# Import config - handle both direct execution and Flask app context
try:
    from config import Config
except ImportError:
    # If running as module, add parent to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import Config

def create_app():
    # Get the root directory (parent of app/)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(root_dir, 'templates')
    static_dir = os.path.join(root_dir, 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.config.from_object(Config)
    
    # Register blueprints
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app

