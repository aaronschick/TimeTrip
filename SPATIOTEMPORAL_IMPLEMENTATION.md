# Spatiotemporal Implementation Summary

## Overview
This implementation adds location support to events, enabling two-way linking between the timeline and globe visualization.

## Changed Files

### Backend

1. **`app/models.py`**
   - Added location fields to `TimelineEvent` model:
     - `lat` (Float, nullable)
     - `lon` (Float, nullable)
     - `location_label` (String, nullable)
     - `geometry` (Text, nullable) - for GeoJSON
     - `location_confidence` (String, default='exact') - enum: 'exact', 'approx', 'disputed'
   - Updated `to_dict()` to include location fields

2. **`app/routes.py`**
   - Updated `add_event()` endpoint to validate and store location fields
   - Updated CSV import to handle location columns (ignores if absent)
   - Updated `/api/timeline` to support location filtering:
     - Query params: `filter_lat`, `filter_lon`, `filter_radius` (km)
     - Uses Haversine formula for distance calculation

3. **`app/timeline.py`**
   - Updated `customdata` arrays to include location fields (indices 9-13)
   - Preserves original dataframe for accurate event counts

4. **`init_db.py`**
   - Updated CSV import logic to parse location fields

5. **`migrate_add_location.py`** (NEW)
   - Safe migration script to add location columns to existing database
   - Checks for column existence before adding

### Frontend

6. **`templates/index.html`**
   - Added location fields to Add Event modal:
     - Location label input
     - Latitude/Longitude inputs (side by side)
     - Location confidence dropdown
     - Advanced GeoJSON textarea (collapsible)
   - Added map filter controls UI below Earth view

7. **`static/css/style.css`**
   - Added `.form-section` and `.form-row` styles for location fields

8. **`static/js/main.js`**
   - Updated `handleAddEvent()` to collect location fields
   - Updated `populateEventDetails()` to:
     - Parse location from customdata (indices 9-13)
     - Display location in Event Details sidebar
     - Center globe on event location if available
   - Added `centerGlobeOnLocation()` function for precise location centering
   - Added `appState` object for state management:
     - `selectedEvent`: Currently selected event
     - `mapFilter`: Active location filter
     - `mapSelectionMode`: UI state
   - Updated `loadTimeline()` to include location filter in API call
   - Added map filter functions:
     - `toggleMapSelectionMode()`: Show/hide filter controls
     - `applyMapFilter()`: Apply location filter to timeline
     - `clearMapFilter()`: Remove filter and reload timeline

## Database Migration

Run the migration script to add location columns to existing database:

```bash
python migrate_add_location.py
```

This script safely adds columns only if they don't exist, so it's safe to run multiple times.

## Testing Guide

### 1. Database Migration
```bash
python migrate_add_location.py
```
Verify columns were added (should see "✓" messages).

### 2. Add Event with Location
1. Click "Add Event" button
2. Fill in required fields (Title, Category, Start Year)
3. Scroll to "Location (Optional)" section
4. Enter:
   - Location Label: "Rome, Italy"
   - Latitude: 41.9028
   - Longitude: 12.4964
   - Location Confidence: "exact"
5. Click "Add Event"
6. Verify event appears in timeline

### 3. Timeline → Globe Linking
1. Click any event point on the timeline
2. Verify:
   - Event Details sidebar shows location information
   - Globe centers on event location (if lat/lon present)
   - If no location, globe shows continent view

### 4. Globe → Timeline Filtering
1. Click "📍 Select Location" button on Earth view
2. Map filter controls appear
3. Enter coordinates:
   - Latitude: 40.0
   - Longitude: -74.0
   - Radius: 1000 (km)
4. Click "Apply Filter"
5. Verify:
   - Timeline reloads showing only events within radius
   - Globe centers on filter location
   - Filter indicator appears

### 5. Clear Filter
1. Click "✕ Clear Filter" button
2. Verify:
   - Timeline reloads with all events
   - Filter controls hide
   - Globe returns to previous view

### 6. CSV Import with Location
1. Create/update CSV with location columns:
   ```csv
   id,title,category,start_year,lat,lon,location_label,location_confidence
   test-1,Test Event,war,1000,41.9028,12.4964,Rome,exact
   ```
2. Use "Import CSV" feature
3. Verify events import with location data

### 7. Existing Features Still Work
- Search events ✓
- Update/Reset timeline ✓
- Manage Events modal ✓
- Delete events ✓
- All CRUD operations ✓

## API Changes

### New Query Parameters for `/api/timeline`
- `filter_lat` (float): Filter events by latitude
- `filter_lon` (float): Filter events by longitude  
- `filter_radius` (float, default=500): Radius in kilometers

Example:
```
/api/timeline?start_year=-1000&end_year=2000&filter_lat=41.9028&filter_lon=12.4964&filter_radius=1000
```

## Data Model

### Location Fields Schema
- `lat`: Float, nullable, range: -90 to 90
- `lon`: Float, nullable, range: -180 to 180
- `location_label`: String(500), nullable
- `geometry`: Text, nullable (GeoJSON string)
- `location_confidence`: String(20), default='exact', values: 'exact', 'approx', 'disputed'

### Customdata Array Format
Events in timeline customdata now include:
```
[id, title, category, continent, start_year, end_year, start_date, end_date, description, lat, lon, location_label, geometry, location_confidence]
```

## Notes

- Location fields are optional - existing events work without them
- CSV import gracefully handles missing location columns
- Globe uses Google Maps embed (iframe) - direct click events not supported, so manual coordinate input is provided
- Location filtering uses Haversine formula for accurate distance calculation
- State is maintained in `window.appState` for consistent UI behavior

## Future Enhancements

- GeoJSON geometry support for region-based filtering
- Interactive map selection using Google Maps API (requires API key)
- Location autocomplete/search
- Multiple location filters
- Export filtered events

