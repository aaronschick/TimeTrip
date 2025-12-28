# Database Setup Guide

TimeTrip now uses a database for data persistence. The app supports both SQLite (for local development) and PostgreSQL (for production).

## Local Development (SQLite)

SQLite is used automatically when no `DATABASE_URL` environment variable is set. No setup required!

1. **Initialize the database:**
   ```bash
   python init_db.py
   ```

2. **Import CSV data (optional):**
   ```bash
   python init_db.py --csv timeline_data_4.csv
   ```

The database file (`timetrip.db`) will be created in the project root.

## Production (PostgreSQL on Render)

### Step 1: Create PostgreSQL Database on Render

1. Go to your Render dashboard
2. Click "New +" → "PostgreSQL"
3. Configure:
   - **Name**: `timetrip-db` (or any name)
   - **Database**: `timetrip` (or any name)
   - **User**: Auto-generated
   - **Region**: Choose closest to your web service
4. Click "Create Database"
5. **Note the connection string** - it will look like:
   ```
   postgres://user:password@hostname:5432/database
   ```

### Step 2: Link Database to Web Service

1. Go to your web service settings
2. Under "Environment", add an environment variable:
   - **Key**: `DATABASE_URL`
   - **Value**: The connection string from Step 1
3. Save changes

### Step 3: Initialize Database

After deploying, you have two options:

**Option A: Use the web interface**
- The database tables will be created automatically on first run
- Use the "Add Event" button to add events manually

**Option B: Import CSV data (recommended)**
1. SSH into your Render service (if available) or use a one-off command
2. Run the initialization script:
   ```bash
   python init_db.py --csv timeline_data_4.csv
   ```

**Note**: Render's free tier doesn't support SSH. You can:
- Add a temporary route to import data via web interface
- Use Render's "Shell" feature (if available)
- Import data manually through the web interface

## Manual Database Initialization

If you need to initialize the database manually:

```python
from app import create_app
from app.models import db

app = create_app()
with app.app_context():
    db.create_all()
    print("Database initialized!")
```

## Importing CSV Data

To import your existing CSV data:

```bash
python init_db.py --csv path/to/your/file.csv
```

Or programmatically:

```python
from init_db import import_csv_data
import_csv_data('timeline_data_4.csv')
```

## Database Schema

The `timeline_events` table has the following structure:

- `id` (String, Primary Key): Unique event identifier
- `title` (String): Event title
- `category` (String): Event category
- `continent` (String): Geographic region
- `start_year` (BigInteger): Start year (can be negative for BCE)
- `end_year` (BigInteger): End year
- `description` (Text): Event description (optional)
- `start_date` (Date): Precise start date (optional)
- `end_date` (Date): Precise end date (optional)
- `created_at` (DateTime): When the event was created
- `updated_at` (DateTime): When the event was last updated

## Troubleshooting

### Database connection errors

- **Check DATABASE_URL**: Ensure the environment variable is set correctly
- **Check credentials**: Verify username, password, and database name
- **Check network**: Ensure your web service can reach the database (same region recommended)

### Migration from CSV

If you're migrating from CSV:
1. Backup your CSV file
2. Run `python init_db.py --csv timeline_data_4.csv`
3. Verify data in the web interface

### Empty database

If your database is empty:
1. Check if tables exist: Visit `/api/debug` endpoint
2. Import data: Run `python init_db.py --csv timeline_data_4.csv`
3. Or add events manually through the web interface

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (for production)
  - Format: `postgresql://user:password@host:port/database`
  - If not set, uses SQLite for local development

