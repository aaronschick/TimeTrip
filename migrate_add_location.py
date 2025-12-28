#!/usr/bin/env python3
"""
Migration script to add location fields to timeline_events table
This script safely adds new columns if they don't exist
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from sqlalchemy import text, inspect

def migrate_add_location_fields():
    """Add location fields to timeline_events table if they don't exist"""
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('timeline_events')]
        
        print("Checking database schema...")
        
        # Add columns if they don't exist
        if 'lat' not in columns:
            print("Adding 'lat' column...")
            db.session.execute(text("ALTER TABLE timeline_events ADD COLUMN lat FLOAT"))
            db.session.commit()
            print("  ✓ Added 'lat' column")
        else:
            print("  ✓ 'lat' column already exists")
        
        if 'lon' not in columns:
            print("Adding 'lon' column...")
            db.session.execute(text("ALTER TABLE timeline_events ADD COLUMN lon FLOAT"))
            db.session.commit()
            print("  ✓ Added 'lon' column")
        else:
            print("  ✓ 'lon' column already exists")
        
        if 'location_label' not in columns:
            print("Adding 'location_label' column...")
            db.session.execute(text("ALTER TABLE timeline_events ADD COLUMN location_label VARCHAR(500)"))
            db.session.commit()
            print("  ✓ Added 'location_label' column")
        else:
            print("  ✓ 'location_label' column already exists")
        
        if 'geometry' not in columns:
            print("Adding 'geometry' column...")
            db.session.execute(text("ALTER TABLE timeline_events ADD COLUMN geometry TEXT"))
            db.session.commit()
            print("  ✓ Added 'geometry' column")
        else:
            print("  ✓ 'geometry' column already exists")
        
        if 'location_confidence' not in columns:
            print("Adding 'location_confidence' column...")
            db.session.execute(text("ALTER TABLE timeline_events ADD COLUMN location_confidence VARCHAR(20) DEFAULT 'exact'"))
            db.session.commit()
            print("  ✓ Added 'location_confidence' column")
        else:
            print("  ✓ 'location_confidence' column already exists")
        
        print("\nMigration complete!")

if __name__ == '__main__':
    migrate_add_location_fields()

