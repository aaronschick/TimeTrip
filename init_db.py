#!/usr/bin/env python3
"""
Initialize database and optionally import CSV data
"""
import sys
import os
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, TimelineEvent
from config import Config

def init_database():
    """Initialize database tables"""
    app = create_app()
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        return app

def import_csv_data(csv_path=None):
    """Import data from CSV file into database"""
    if csv_path is None:
        csv_path = Config.TIMELINE_DATA_FILE
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return False
    
    app = create_app()
    with app.app_context():
        # Check if data already exists
        existing_count = TimelineEvent.query.count()
        if existing_count > 0:
            response = input(f"Database already contains {existing_count} events. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Import cancelled.")
                return False
            print("Clearing existing data...")
            TimelineEvent.query.delete()
            db.session.commit()
        
        print(f"Reading CSV file: {csv_path}")
        df = pd.read_csv(csv_path)
        df = df.dropna(axis=1, how='all')  # Remove empty columns
        
        print(f"Importing {len(df)} events...")
        
        imported = 0
        skipped = 0
        
        for _, row in df.iterrows():
            try:
                # Skip rows with missing required fields
                if pd.isna(row.get('id')) or pd.isna(row.get('title')) or pd.isna(row.get('start_year')):
                    skipped += 1
                    continue
                
                # Parse dates
                start_date = None
                end_date = None
                
                if 'start_date' in row and pd.notna(row['start_date']):
                    try:
                        start_date = pd.to_datetime(row['start_date'], errors='coerce')
                        if pd.notna(start_date):
                            start_date = start_date.date()
                        else:
                            start_date = None
                    except:
                        start_date = None
                
                if 'end_date' in row and pd.notna(row['end_date']):
                    try:
                        end_date = pd.to_datetime(row['end_date'], errors='coerce')
                        if pd.notna(end_date):
                            end_date = end_date.date()
                        else:
                            end_date = None
                    except:
                        end_date = None
                
                # Create event
                event = TimelineEvent(
                    id=str(row['id']).strip(),
                    title=str(row['title']).strip(),
                    category=str(row.get('category', 'other')).strip(),
                    continent=str(row.get('continent', 'Global')).strip(),
                    start_year=int(row['start_year']),
                    end_year=int(row.get('end_year', row['start_year'])),
                    description=str(row.get('description', '')).strip() if pd.notna(row.get('description')) else None,
                    start_date=start_date,
                    end_date=end_date
                )
                
                db.session.add(event)
                imported += 1
                
                # Commit in batches
                if imported % 50 == 0:
                    db.session.commit()
                    print(f"  Imported {imported} events...")
                    
            except Exception as e:
                print(f"  Error importing row {row.get('id', 'unknown')}: {e}")
                skipped += 1
                continue
        
        # Final commit
        db.session.commit()
        
        print(f"\nImport complete!")
        print(f"  Imported: {imported} events")
        print(f"  Skipped: {skipped} events")
        
        return True

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize database and import CSV data')
    parser.add_argument('--csv', help='Path to CSV file to import', default=None)
    parser.add_argument('--init-only', action='store_true', help='Only initialize database, do not import CSV')
    
    args = parser.parse_args()
    
    # Initialize database
    app = init_database()
    
    # Import CSV if requested
    if not args.init_only:
        csv_path = args.csv or Config.TIMELINE_DATA_FILE
        if os.path.exists(csv_path):
            import_csv_data(csv_path)
        else:
            print(f"\nCSV file not found at {csv_path}")
            print("Database initialized. You can add events through the web interface.")
    else:
        print("\nDatabase initialized. You can add events through the web interface.")

