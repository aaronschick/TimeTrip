"""
Configuration settings for Chronoverse application
"""
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Data file path - using the original timeline_data_4.csv file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TIMELINE_DATA_FILE = os.path.join(BASE_DIR, 'timeline_data_4.csv')
    
    # For production deployments (like Render), files in the repo are read-only
    # Changes will be lost on redeploy. Consider using a database for persistence.
    # For now, we'll try to write to the original file, but handle errors gracefully.
    
    # Server settings
    PORT = int(os.environ.get('PORT', 5001))  # Default to 5001 to avoid AirPlay conflict on macOS
    
    # Timeline settings
    DEFAULT_START_YEAR = -5_000_000_000
    DEFAULT_END_YEAR = 2025
    RECENT_MIN_YEAR = 1678  # pandas.Timestamp min year
    RECENT_MAX_YEAR = 2262  # pandas.Timestamp max year
    
    # Category order for timeline
    CATEGORY_ORDER = ["era", "migration", "civilization", "empire", "war", "religion", "biblical"]

