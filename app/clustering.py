"""
Semantic Zoom and Clustering Module

Defines zoom tiers and implements event clustering for timeline visualization.
Clustering groups events into time buckets when zoomed out to maintain readability.
"""
import pandas as pd
import numpy as np

# Zoom Tier Definitions
# Based on visible time range (in years)
ZOOM_TIERS = {
    0: {
        'min_range': 500_000_000,  # > 500M years (deep time, only major anchors)
        'bucket_size': 50_000_000,  # 50M year buckets
        'show_categories': ['era'],  # Only show major eras
        'label_density': 'sparse',  # Very few labels
        'cluster_threshold': 5  # Cluster if >5 events per bucket
    },
    1: {
        'min_range': 50_000_000,  # 50M-500M years
        'bucket_size': 5_000_000,  # 5M year buckets
        'show_categories': ['era', 'civilization'],  # Major categories
        'label_density': 'medium',
        'cluster_threshold': 10
    },
    2: {
        'min_range': 500_000,  # 500k-50M years
        'bucket_size': 500_000,  # 500k year buckets
        'show_categories': ['era', 'civilization', 'empire'],
        'label_density': 'medium',
        'cluster_threshold': 15
    },
    3: {
        'min_range': 5_000,  # 5k-500k years
        'bucket_size': 1_000,  # 1k year buckets
        'show_categories': None,  # Show all categories
        'label_density': 'dense',
        'cluster_threshold': 20
    },
    4: {
        'min_range': 0,  # < 5k years (human history detail)
        'bucket_size': 100,  # 100 year buckets
        'show_categories': None,  # Show all
        'label_density': 'very_dense',
        'cluster_threshold': 25
    }
}

def get_zoom_tier(time_range):
    """
    Determine zoom tier based on visible time range.
    
    Args:
        time_range: Difference between end_year and start_year (in years)
    
    Returns:
        int: Zoom tier (0-4)
    """
    for tier in sorted(ZOOM_TIERS.keys(), reverse=True):
        if time_range >= ZOOM_TIERS[tier]['min_range']:
            return tier
    return 4  # Default to most detailed tier

def should_cluster(tier, event_count, time_range):
    """
    Determine if clustering should be applied.
    
    Args:
        tier: Zoom tier (0-4)
        event_count: Number of events in the visible range
        time_range: Visible time range in years
    
    Returns:
        bool: True if clustering should be applied
    """
    tier_config = ZOOM_TIERS[tier]
    threshold = tier_config['cluster_threshold']
    
    # Calculate average events per bucket
    bucket_size = tier_config['bucket_size']
    num_buckets = max(1, int(time_range / bucket_size))
    avg_per_bucket = event_count / num_buckets if num_buckets > 0 else 0
    
    return avg_per_bucket > threshold

def cluster_events(df, start_year, end_year, tier, enable_clustering=True):
    """
    Cluster events into time buckets based on zoom tier.
    
    Args:
        df: DataFrame with events (must have 'year', 'category', 'continent', 'id', 'title')
        start_year: Start of visible range
        end_year: End of visible range
        tier: Zoom tier (0-4)
        enable_clustering: Whether to actually cluster (can be toggled off)
    
    Returns:
        tuple: (clustered_df, cluster_info_dict)
            - clustered_df: DataFrame with cluster markers or individual events
            - cluster_info_dict: Dict mapping cluster_id -> list of event data
    """
    if df.empty or not enable_clustering:
        return df, {}
    
    time_range = end_year - start_year
    tier_config = ZOOM_TIERS[tier]
    bucket_size = tier_config['bucket_size']
    
    # Filter by category if tier specifies limited categories
    if tier_config['show_categories'] is not None:
        df_filtered = df[df['category'].isin(tier_config['show_categories'])].copy()
        df_other = df[~df['category'].isin(tier_config['show_categories'])].copy()
    else:
        df_filtered = df.copy()
        df_other = pd.DataFrame()
    
    # Ensure 'year' column exists (representative year for clustering)
    if 'year' not in df_filtered.columns:
        # Use midpoint of start_year and end_year, or just start_year
        df_filtered['year'] = df_filtered.apply(
            lambda row: (row['start_year'] + row['end_year']) / 2 if pd.notna(row.get('end_year')) and row['end_year'] != row['start_year'] else row['start_year'],
            axis=1
        )
    
    # Calculate bucket for each event
    # Bucket is based on the event's representative year (midpoint of start/end or just year)
    df_filtered = df_filtered.copy()
    df_filtered['bucket'] = ((df_filtered['year'] - start_year) // bucket_size).astype(int)
    
    # Group by bucket, category, and continent
    cluster_info = {}
    clustered_rows = []
    
    for (bucket, category, continent), group in df_filtered.groupby(['bucket', 'category', 'continent']):
        if len(group) >= tier_config['cluster_threshold']:
            # Create a cluster
            bucket_start = start_year + (bucket * bucket_size)
            bucket_end = min(end_year, bucket_start + bucket_size)
            cluster_id = f"cluster_{bucket}_{category}_{continent}"
            
            # Representative point for cluster (center of bucket)
            cluster_year = bucket_start + (bucket_size / 2)
            
            # Store cluster info
            cluster_info[cluster_id] = {
                'bucket_start': bucket_start,
                'bucket_end': bucket_end,
                'category': category,
                'continent': continent,
                'event_count': len(group),
                'events': group[['id', 'title', 'start_year', 'end_year', 'category', 'continent', 
                                'lat', 'lon', 'location_label', 'geometry', 'location_confidence']].to_dict('records')
            }
            
            # Create cluster marker row
            # Ensure all required columns exist
            cluster_row = {
                'id': cluster_id,
                'title': f"{len(group)} events",
                'category': category,
                'continent': continent,
                'start_year': int(bucket_start),
                'end_year': int(bucket_end),
                'year': cluster_year,
                'description': f"Cluster: {len(group)} events in {category} category",
                'is_cluster': True,
                'cluster_id': cluster_id
            }
            # Add location fields if any event in cluster has location
            for _, event_row in group.iterrows():
                if 'lat' in event_row and pd.notna(event_row['lat']):
                    cluster_row['lat'] = float(event_row['lat'])
                    break
            for _, event_row in group.iterrows():
                if 'lon' in event_row and pd.notna(event_row['lon']):
                    cluster_row['lon'] = float(event_row['lon'])
                    break
            clustered_rows.append(cluster_row)
        else:
            # Keep individual events
            for _, row in group.iterrows():
                row_dict = row.to_dict()
                row_dict['is_cluster'] = False
                # Ensure 'year' column exists
                if 'year' not in row_dict or pd.isna(row_dict.get('year')):
                    if pd.notna(row_dict.get('start_year')) and pd.notna(row_dict.get('end_year')):
                        row_dict['year'] = (row_dict['start_year'] + row_dict['end_year']) / 2
                    elif pd.notna(row_dict.get('start_year')):
                        row_dict['year'] = row_dict['start_year']
                clustered_rows.append(row_dict)
    
    # Add events from other categories (not filtered by tier)
    if not df_other.empty:
        for _, row in df_other.iterrows():
            row_dict = row.to_dict()
            row_dict['is_cluster'] = False
            # Ensure 'year' column exists
            if 'year' not in row_dict or pd.isna(row_dict.get('year')):
                if pd.notna(row_dict.get('start_year')) and pd.notna(row_dict.get('end_year')):
                    row_dict['year'] = (row_dict['start_year'] + row_dict['end_year']) / 2
                elif pd.notna(row_dict.get('start_year')):
                    row_dict['year'] = row_dict['start_year']
            clustered_rows.append(row_dict)
    
    clustered_df = pd.DataFrame(clustered_rows)
    
    # Ensure 'year' column exists in final dataframe
    if not clustered_df.empty and 'year' not in clustered_df.columns:
        clustered_df['year'] = clustered_df.apply(
            lambda row: (row['start_year'] + row['end_year']) / 2 if pd.notna(row.get('end_year')) and row['end_year'] != row['start_year'] else row['start_year'],
            axis=1
        )
    
    return clustered_df, cluster_info

