"""
Configuration settings for Chronoverse application
"""
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration
    # For local development, use SQLite (no setup required)
    # For production (Render), use PostgreSQL from DATABASE_URL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # Production: PostgreSQL from Render or other provider
        # Replace postgres:// with postgresql:// for SQLAlchemy compatibility
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Development: SQLite (fallback)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "timetrip.db")}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Legacy CSV file path (for migration purposes)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TIMELINE_DATA_FILE = os.path.join(BASE_DIR, 'timeline_data_4.csv')
    
    # Server settings
    PORT = int(os.environ.get('PORT', 5001))  # Default to 5001 to avoid AirPlay conflict on macOS
    
    # Timeline settings
    DEFAULT_START_YEAR = -5_000_000_000
    DEFAULT_END_YEAR = 2025
    RECENT_MIN_YEAR = 1678  # pandas.Timestamp min year
    RECENT_MAX_YEAR = 2262  # pandas.Timestamp max year
    
    # Category order for timeline
    CATEGORY_ORDER = ["era", "migration", "civilization", "empire", "war", "religion", "biblical"]

