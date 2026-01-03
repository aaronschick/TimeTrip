#!/usr/bin/env python3
"""
Export all timeline events from database to CSV file
"""
import sys
import os
import csv
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, TimelineEvent

def export_to_csv(output_file='timeline_events_export.csv'):
    """Export all timeline events to CSV"""
    app = create_app()
    with app.app_context():
        # Query all events
        events = TimelineEvent.query.order_by(TimelineEvent.start_year).all()
        
        if not events:
            print("No events found in database.")
            return False
        
        print(f"Exporting {len(events)} events to {output_file}...")
        
        # Define CSV columns matching the database schema
        fieldnames = [
            'id',
            'title',
            'category',
            'continent',
            'start_year',
            'end_year',
            'description',
            'start_date',
            'end_date',
            'lat',
            'lon',
            'location_label',
            'geometry',
            'location_confidence'
        ]
        
        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for event in events:
                row = {
                    'id': event.id,
                    'title': event.title,
                    'category': event.category,
                    'continent': event.continent or 'Global',
                    'start_year': event.start_year,
                    'end_year': event.end_year,
                    'description': event.description or '',
                    'start_date': event.start_date.isoformat() if event.start_date else '',
                    'end_date': event.end_date.isoformat() if event.end_date else '',
                    'lat': event.lat if event.lat is not None else '',
                    'lon': event.lon if event.lon is not None else '',
                    'location_label': event.location_label or '',
                    'geometry': event.geometry or '',
                    'location_confidence': event.location_confidence or 'exact'
                }
                writer.writerow(row)
        
        print(f"Successfully exported {len(events)} events to {output_file}")
        return True

if __name__ == '__main__':
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'timeline_events_export.csv'
    export_to_csv(output_file)

