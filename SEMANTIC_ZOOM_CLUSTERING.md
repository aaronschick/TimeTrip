# Semantic Zoom & Clustering Implementation

## Overview

This implementation adds semantic zoom and event clustering to the timeline visualization, enabling it to handle 10x more events while maintaining readability. Events are automatically clustered when zoomed out, and clusters can be expanded by clicking.

## How It Works

### A) Zoom Tiers (Semantic Zoom)

The system defines 5 zoom tiers based on the visible time range:

- **Tier 0**: > 500M years (deep time)
  - Bucket size: 50M years
  - Shows only: `era` category
  - Cluster threshold: 5 events/bucket
  - Label density: sparse

- **Tier 1**: 50M - 500M years
  - Bucket size: 5M years
  - Shows: `era`, `civilization`
  - Cluster threshold: 10 events/bucket
  - Label density: medium

- **Tier 2**: 500k - 50M years
  - Bucket size: 500k years
  - Shows: `era`, `civilization`, `empire`
  - Cluster threshold: 15 events/bucket
  - Label density: medium

- **Tier 3**: 5k - 500k years
  - Bucket size: 1k years
  - Shows: all categories
  - Cluster threshold: 20 events/bucket
  - Label density: dense

- **Tier 4**: < 5k years (human history)
  - Bucket size: 100 years
  - Shows: all categories
  - Cluster threshold: 25 events/bucket
  - Label density: very dense

### B) Clustering Logic

1. **Automatic Clustering**: When the visible time range triggers clustering (based on tier and event density), events are grouped into time buckets.

2. **Bucket Calculation**: Events are assigned to buckets based on their representative year (midpoint of start/end year).

3. **Cluster Formation**: Events in the same bucket, category, and continent are grouped if they exceed the tier's threshold.

4. **Cluster Rendering**: Clusters appear as diamond-shaped markers (larger, gold-bordered) distinct from individual events.

5. **Cluster Expansion**: Clicking a cluster:
   - Zooms the timeline into that cluster's time range
   - Temporarily disables clustering for that view
   - Shows a preview of events in the sidebar (top 10)
   - Clustering re-enables automatically when zooming back out

### C) User Controls

- **Clusters Toggle Button**: "Clusters: On/Off" button in the controls panel
  - When OFF: All events shown individually (no clustering)
  - When ON: Clustering applied automatically based on zoom level

## Implementation Details

### Backend (`app/clustering.py`)

- `get_zoom_tier(time_range)`: Determines zoom tier from time range
- `should_cluster(tier, event_count, time_range)`: Decides if clustering is needed
- `cluster_events(df, start_year, end_year, tier, enable_clustering)`: Performs clustering

### Backend (`app/timeline.py`)

- Modified `make_figure_json()` to:
  - Determine zoom tier
  - Apply clustering if needed
  - Render clusters as separate traces (diamond markers)
  - Include cluster info in response metadata

### Backend (`app/routes.py`)

- Added `enable_clustering` query parameter to `/api/timeline`
- Defaults to `true` (clustering enabled)

### Frontend (`static/js/main.js`)

- Added `clusteringEnabled` state variable
- `toggleClustering()`: Toggles clustering on/off
- `handlePlotlyClick()`: Detects cluster clicks and expands them
- `expandCluster(clusterId)`: Zooms into cluster time range
- `showClusterPreview(cluster)`: Displays cluster contents in sidebar

### Frontend (`templates/index.html`)

- Added "Clusters: On/Off" toggle button

## Changed Files

1. **`app/clustering.py`** (NEW): Zoom tier definitions and clustering logic
2. **`app/timeline.py`**: Integrated clustering into figure generation
3. **`app/routes.py`**: Added clustering parameter to API endpoint
4. **`static/js/main.js`**: Cluster expansion and toggle functionality
5. **`templates/index.html`**: Added clusters toggle button
6. **`static/css/style.css`**: Added `.btn-warning` style for toggle state

## Testing

### Test Clustering Activation

1. Set a very wide time range (e.g., -5B to 2025)
2. Verify clusters appear as diamond markers
3. Check that clusters show event counts in hover text

### Test Cluster Expansion

1. Click on a cluster marker
2. Verify timeline zooms into cluster's time range
3. Check that sidebar shows cluster preview with event list
4. Verify individual events appear in the zoomed view

### Test Toggle

1. Click "Clusters: On" button → should change to "Clusters: Off"
2. Timeline should reload showing all individual events
3. Click again → should re-enable clustering

### Test Existing Features

- Search events ✓
- Add/Edit/Delete events ✓
- Import CSV ✓
- Location filtering ✓
- Timeline → Globe linking ✓
- All modals and UI controls ✓

## Customdata Format

Events now include cluster information in customdata (indices 14-15):
- Index 14: `is_cluster` (boolean)
- Index 15: `cluster_id` (string, if cluster)

Full customdata array (16 elements):
```
[id, title, category, continent, start_year, end_year, start_date, end_date, 
 description, lat, lon, location_label, geometry, location_confidence, 
 is_cluster, cluster_id]
```

## Performance Notes

- Clustering is performed on the backend, reducing frontend processing
- Cluster info is included in API response metadata for efficient expansion
- Clustering automatically adjusts based on zoom level
- No performance impact when clustering is disabled

## Future Enhancements

- Region-based clustering (GeoJSON geometry)
- Custom cluster thresholds per user preference
- Cluster animation when expanding
- Multiple cluster selection
- Export clustered events

