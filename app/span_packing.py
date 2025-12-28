"""
Span Rendering and Lane Packing Module

Handles rendering events as spans (horizontal bars) with overlap lane packing
to ensure all overlapping spans remain visible.
"""
import pandas as pd
import numpy as np
from app.clustering import get_zoom_tier, ZOOM_TIERS

def should_render_as_span(row, time_range, min_duration_threshold=None):
    """
    Determine if an event should be rendered as a span (bar) or point.
    
    Args:
        row: Event row with start_year and end_year
        time_range: Visible time range (end_year - start_year)
        min_duration_threshold: Minimum duration to render as span (if None, auto-calculate)
    
    Returns:
        bool: True if should render as span
    """
    start_year = row.get('start_year')
    end_year = row.get('end_year')
    
    if pd.isna(start_year) or pd.isna(end_year):
        return False
    
    duration = abs(end_year - start_year)
    
    # If duration is 0 or very small, render as point
    if duration == 0:
        return False
    
    # Auto-calculate threshold based on zoom level
    if min_duration_threshold is None:
        tier = get_zoom_tier(time_range)
        # Threshold: spans must be at least 0.1% of visible range, or 1000 years, whichever is smaller
        threshold = min(time_range * 0.001, 1000)
    else:
        threshold = min_duration_threshold
    
    return duration >= threshold

def pack_intervals(intervals):
    """
    Pack overlapping intervals into lanes using a greedy algorithm.
    
    Args:
        intervals: List of dicts with 'start', 'end', and 'data' keys
            Each interval represents an event span
    
    Returns:
        dict: Mapping of interval index to lane number (0-based)
    """
    if not intervals:
        return {}
    
    # Sort intervals by start time, then by duration (shorter first for better packing)
    sorted_intervals = sorted(enumerate(intervals), key=lambda x: (x[1]['start'], x[1]['end'] - x[1]['start']))
    
    # Track end times for each lane
    lane_ends = []
    lane_assignments = {}
    
    for orig_idx, interval in sorted_intervals:
        start = interval['start']
        end = interval['end']
        
        # Find first lane that doesn't overlap
        assigned_lane = None
        for lane_idx, lane_end in enumerate(lane_ends):
            if lane_end <= start:
                # This lane is free
                assigned_lane = lane_idx
                lane_ends[lane_idx] = end
                break
        
        # If no free lane, create a new one
        if assigned_lane is None:
            assigned_lane = len(lane_ends)
            lane_ends.append(end)
        
        lane_assignments[orig_idx] = assigned_lane
    
    return lane_assignments

def prepare_spans_and_points(df, time_range, category_name):
    """
    Separate events into spans and points, and pack spans into lanes.
    
    Args:
        df: DataFrame with events for a category
        time_range: Visible time range
        category_name: Category name (for y-position)
    
    Returns:
        tuple: (spans_data, points_data)
            spans_data: List of dicts with span info including lane assignment
            points_data: DataFrame with point events
    """
    spans_data = []
    points_mask = []
    
    # Determine which events are spans vs points
    for idx, row in df.iterrows():
        is_span = should_render_as_span(row, time_range)
        points_mask.append(not is_span)
        
        if is_span:
            spans_data.append({
                'index': idx,
                'start': row['start_year'],
                'end': row['end_year'],
                'data': row
            })
    
    # Pack spans into lanes
    if spans_data:
        lane_assignments = pack_intervals(spans_data)
        for span in spans_data:
            span['lane'] = lane_assignments.get(span['index'], 0)
    else:
        lane_assignments = {}
    
    # Separate points
    points_df = df[points_mask].copy() if any(points_mask) else pd.DataFrame()
    
    return spans_data, points_df, lane_assignments

