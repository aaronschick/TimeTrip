#!/usr/bin/env python3
"""
Quick script to verify all events are being loaded and can be plotted
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from app.timeline import TimelineGenerator

print("=" * 60)
print("EVENT VERIFICATION")
print("=" * 60)

# Load data
print(f"\n1. Loading data from: {Config.TIMELINE_DATA_FILE}")
print(f"   File exists: {os.path.exists(Config.TIMELINE_DATA_FILE)}")

timeline_gen = TimelineGenerator(Config.TIMELINE_DATA_FILE)
print(f"   ✓ Loaded {len(timeline_gen.df)} total events")

# Check data quality
print(f"\n2. Data Quality Check:")
print(f"   - Events with valid start_year: {timeline_gen.df['start_year'].notna().sum()}")
print(f"   - Events with valid end_year: {timeline_gen.df['end_year'].notna().sum()}")
print(f"   - Events with valid category: {timeline_gen.df['category'].notna().sum() if 'category' in timeline_gen.df.columns else 'N/A'}")

# Test filtering
print(f"\n3. Testing Filter (default range: -5,000,000,000 to 2025):")
filtered = timeline_gen.get_filtered_data(-5_000_000_000, 2025)
print(f"   - Events in range: {len(filtered)}")
print(f"   - Expected: {len(timeline_gen.df)} (all events should be included)")

if len(filtered) != len(timeline_gen.df):
    print(f"   ⚠️  WARNING: {len(timeline_gen.df) - len(filtered)} events are being filtered out!")
    # Show which events are missing
    all_ids = set(timeline_gen.df['id'].values)
    filtered_ids = set(filtered['id'].values)
    missing = all_ids - filtered_ids
    if missing:
        print(f"   Missing event IDs: {list(missing)[:10]}...")  # Show first 10

# Test figure generation
print(f"\n4. Testing Figure Generation:")
try:
    fig_json = timeline_gen.make_figure_json(-5_000_000_000, 2025)
    num_traces = len(fig_json.get('data', []))
    print(f"   ✓ Figure generated successfully")
    print(f"   - Number of traces: {num_traces}")
    
    # Count total data points
    total_points = 0
    for trace in fig_json.get('data', []):
        if 'x' in trace and trace['x'] is not None:
            total_points += len(trace['x'])
    print(f"   - Total data points in traces: {total_points}")
    print(f"   - Expected data points: {len(filtered)}")
    
    if total_points != len(filtered):
        print(f"   ⚠️  WARNING: {len(filtered) - total_points} data points are missing from the plot!")
        
except Exception as e:
    print(f"   ✗ Error generating figure: {e}")
    import traceback
    traceback.print_exc()

# Show category breakdown
print(f"\n5. Category Breakdown:")
if 'category' in timeline_gen.df.columns:
    cat_counts = timeline_gen.df['category'].value_counts()
    for cat, count in cat_counts.items():
        print(f"   - {cat}: {count} events")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)

