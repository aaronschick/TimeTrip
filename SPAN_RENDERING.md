# Span Rendering with Lane Packing

## Overview

This implementation adds span rendering (horizontal bars) for events with duration, with automatic lane packing to handle overlapping spans. Events are rendered as spans when they have a significant duration relative to the visible time range, and as points for instantaneous events.

**Note**: Span rendering can be toggled on/off via the "Spans: On/Off" button in the UI. When disabled, all events are rendered as points regardless of duration.

## How It Works

### A) Span Detection

Events are rendered as spans (horizontal bars) when:
- `end_year != start_year` (has duration)
- Duration is at least 0.1% of the visible time range, or 1000 years (whichever is smaller)

Events are rendered as points when:
- Duration is 0 or below the threshold
- Very short duration relative to zoom level (collapses to point when zoomed out)

### B) Lane Packing Algorithm

Overlapping spans are automatically packed into lanes within each category using a greedy interval packing algorithm:

1. **Sort intervals** by start time, then by duration (shorter first)
2. **Assign to lanes**: For each interval, find the first lane where the previous interval ends before this one starts
3. **Create new lane** if no existing lane is available
4. **Vertical offset**: Each lane is offset by 0.12 units vertically within the category band

This ensures all overlapping spans remain visible and don't hide each other.

### C) Rendering

- **Spans**: Rendered as `Scatter` traces with `mode='lines+markers'`
  - Horizontal line from start_year to end_year
  - Small markers at endpoints for better clickability
  - Line width: 4px
  - Color: Category color
  
- **Points**: Rendered as `Scatter` traces with `mode='markers'`
  - Single point at event year (or start_year)
  - Marker size: 10px
  - Color: Category color

- **Clusters**: Still rendered as diamond markers (unchanged)

### D) Y-Axis Configuration

The timeline uses numeric y-positions (0, 1, 2, ...) for categories, with custom tick labels showing category names. This allows precise lane offsets while maintaining readable category labels.

### E) Click/Hover Behavior

- **Spans**: Clicking anywhere on the span (line or endpoint markers) shows event details
- **Points**: Clicking the point shows event details
- **Hover**: Shows event title, dates, and description for both spans and points
- **Customdata**: Preserved for both spans and points, enabling full event details display

## Implementation Details

### Backend (`app/span_packing.py`)

- `should_render_as_span(row, time_range, min_duration_threshold)`: Determines if event should be a span
- `pack_intervals(intervals)`: Greedy algorithm to pack overlapping intervals into lanes
- `prepare_spans_and_points(df, time_range, category_name)`: Separates events and packs spans

### Backend (`app/timeline.py`)

- Modified category rendering loop to:
  - Separate spans from points using `prepare_spans_and_points()`
  - Render spans as line traces with lane offsets
  - Render points as marker traces
  - Use numeric y-positions with custom tick labels

### Frontend (`static/js/main.js`)

- Updated `handlePlotlyClick()` to handle both point and span clicks
- Handles customdata arrays for spans (which have data at both endpoints)
- Added `toggleSpans()` function to toggle span rendering mode
- Added `spansEnabled` state variable

## Changed Files

1. **`app/span_packing.py`** (NEW): Span detection and lane packing logic
2. **`app/timeline.py`**: Integrated span rendering with lane packing, added `enable_spans` parameter
3. **`app/routes.py`**: Added `enable_spans` query parameter to `/api/timeline` endpoint
4. **`static/js/main.js`**: Updated click handler for spans, added span toggle functionality
5. **`templates/index.html`**: Added "Spans: On/Off" toggle button

## Testing

### Test Span Rendering

1. Create or find events with `start_year != end_year` (e.g., wars, empires, eras)
2. View timeline with appropriate zoom level
3. Verify events appear as horizontal bars (spans)
4. Verify hover shows start and end years

### Test Lane Packing

1. Find or create overlapping events in the same category
2. View timeline
3. Verify overlapping spans stack vertically in lanes
4. Verify all spans are visible (none hidden)

### Test Point Rendering

1. Find or create events with `start_year == end_year` or very short duration
2. View timeline
3. Verify events appear as points (not spans)
4. Verify hover and click work correctly

### Test Semantic Zoom Integration

1. View timeline with very wide range (e.g., -5B to 2025)
2. Verify short-duration events collapse to points
3. Zoom into a narrower range
4. Verify those events become spans again

### Test Span Toggle

1. Click "Spans: On" button → should change to "Spans: Off"
2. Timeline should reload showing all events as points (no spans)
3. Click again → should re-enable spans
4. Verify events with duration appear as spans when enabled

### Test Existing Features

- Click spans → shows event details ✓
- Click points → shows event details ✓
- Hover on spans → shows event info ✓
- Hover on points → shows event info ✓
- Search/filter/modals/import → all preserved ✓
- Clustering → still works ✓
- Span toggle → works independently of clustering ✓

## Performance Notes

- Lane packing is O(n log n) due to sorting, efficient for thousands of events
- Each span creates one trace (for proper hover/click), but Plotly handles this efficiently
- Lane offsets are small (0.12 units) to keep visual spacing tight
- No performance impact when all events are points (no spans)

## Visual Design

- **Span line width**: 4px (clearly visible but not overwhelming)
- **Lane offset**: 0.12 units (tight stacking, all visible)
- **Endpoint markers**: 6px (subtle, improves clickability)
- **Point markers**: 10px (unchanged from original)
- **Colors**: Category-based (unchanged from original)

## Future Enhancements

- Configurable span threshold per user preference
- Span fill color with opacity for better visibility
- Span labels on hover/click
- Animation when spans appear/disappear on zoom
- Span grouping by category with collapsible lanes

