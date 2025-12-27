#!/usr/bin/env python3
"""
Quick test script to verify data loading
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from app.timeline import TimelineGenerator

print("Testing data loading...")
print(f"Data file: {Config.TIMELINE_DATA_FILE}")
print(f"File exists: {os.path.exists(Config.TIMELINE_DATA_FILE)}")
print()

# Load data
try:
    timeline_gen = TimelineGenerator(Config.TIMELINE_DATA_FILE)
    print(f"✓ Successfully loaded {len(timeline_gen.df)} rows")
    print(f"✓ Columns: {list(timeline_gen.df.columns)}")
    print()
    
    # Test filtering
    filtered = timeline_gen.get_filtered_data(-5_000_000_000, 2025)
    print(f"✓ Filtered data: {len(filtered)} rows for range -5,000,000,000 to 2025")
    print()
    
    # Show sample
    print("Sample data (first 3 rows):")
    print(filtered[['title', 'category', 'start_year', 'end_year']].head(3))
    print()
    
    # Test figure generation
    print("Testing figure generation...")
    fig_json = timeline_gen.make_figure_json(-5_000_000_000, 2025)
    print(f"✓ Figure generated successfully")
    print(f"✓ Number of traces: {len(fig_json.get('data', []))}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

