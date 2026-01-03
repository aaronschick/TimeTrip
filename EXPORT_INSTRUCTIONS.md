# Database Export Instructions

## Export Current Database to CSV

The script `export_db_to_csv.py` exports all timeline events from your database to a CSV file.

### Usage

**For local database (SQLite):**
```bash
python3 export_db_to_csv.py timeline_events_export.csv
```

**For remote database (Render/PostgreSQL):**
```bash
# Set your DATABASE_URL environment variable first
export DATABASE_URL="postgresql://user:password@host:port/database"
python3 export_db_to_csv.py timeline_events_export.csv
```

Or on Windows:
```cmd
set DATABASE_URL=postgresql://user:password@host:port/database
python export_db_to_csv.py timeline_events_export.csv
```

### Output

The script will create a CSV file with all events from your database, including:
- All required fields (id, title, category, start_year, end_year)
- All optional fields (description, dates, location data, etc.)
- Events are sorted by start_year

### Example Output File

The CSV file will be named `timeline_events_export.csv` (or whatever you specify) and will contain all current database records in the same format as the import template.

### Notes

- The script connects to the database using the same configuration as your app
- Empty/null fields will be exported as empty strings in the CSV
- Date fields are exported in ISO format (YYYY-MM-DD)
- The script preserves all data exactly as stored in the database

