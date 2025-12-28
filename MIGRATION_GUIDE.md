# Migration Guide: Adding Location Fields

## Running the Migration Locally

### Step 1: Activate Your Virtual Environment (if using one)

If you're using a virtual environment:

```bash
# Navigate to your project directory
cd /Users/aschick/Documents/repositories/TimeTrip

# Activate virtual environment (if you have one)
# For venv:
source venv/bin/activate

# Or for conda:
# conda activate timetrip
```

### Step 2: Run the Migration Script

The migration script will safely add location columns to your database:

```bash
python migrate_add_location.py
```

**Expected Output:**
```
Checking database schema...
Adding 'lat' column...
  ✓ Added 'lat' column
Adding 'lon' column...
  ✓ Added 'lon' column
Adding 'location_label' column...
  ✓ Added 'location_label' column
Adding 'geometry' column...
  ✓ Added 'geometry' column
Adding 'location_confidence' column...
  ✓ Added 'location_confidence' column

Migration complete!
```

**Note:** If columns already exist, you'll see "✓ [column] already exists" messages. This is safe - the script is idempotent.

### Step 3: Verify Migration

You can verify the migration worked by:

1. **Check the database directly** (if using SQLite):
   ```bash
   sqlite3 timetrip.db ".schema timeline_events"
   ```

2. **Or start your Flask app and check**:
   ```bash
   python run.py
   ```
   Then try adding an event with location data through the web interface.

## Pushing Changes to GitHub

### Step 1: Review Your Changes

Check what files have been modified:

```bash
git status
```

You should see:
- Modified files: `app/models.py`, `app/routes.py`, `app/timeline.py`, `init_db.py`, `templates/index.html`, `static/css/style.css`, `static/js/main.js`
- New files: `migrate_add_location.py`, `SPATIOTEMPORAL_IMPLEMENTATION.md`, `MIGRATION_GUIDE.md`

### Step 2: Stage All Changes

```bash
# Stage all modified and new files
git add .

# Or stage specific files:
git add app/models.py app/routes.py app/timeline.py
git add migrate_add_location.py
git add templates/index.html static/css/style.css static/js/main.js
git add *.md
```

### Step 3: Commit Changes

```bash
git commit -m "Add spatiotemporal location support with two-way timeline-globe linking

- Extended TimelineEvent model with location fields (lat, lon, location_label, geometry, location_confidence)
- Added safe database migration script
- Updated CSV import to handle location columns
- Added location validation in backend API
- Updated timeline JSON to include location in customdata
- Added location fields to Add Event modal UI
- Display location in Event Details sidebar
- Implemented Timeline → Globe: click event centers globe on location
- Implemented Globe → Timeline: map selection filters timeline by location
- Added state management for selected event and map filter
- All existing features preserved and working"
```

### Step 4: Push to GitHub

```bash
# Push to your main/master branch
git push origin main

# Or if your default branch is master:
# git push origin master
```

## Running Migration on Render (Production)

**Important:** On Render, you typically can't run scripts directly. Instead:

### Option 1: Migration Runs Automatically (Recommended)

The migration script uses SQL `ALTER TABLE` statements that are safe to run multiple times. You can:

1. **Add migration to your deployment process:**
   - Add a build command that runs the migration
   - Or run it manually via Render's shell (if available)

2. **Or let SQLAlchemy handle it:**
   - When you deploy, SQLAlchemy will detect the new columns in the model
   - However, you may need to run the migration manually the first time

### Option 2: Run Migration via Render Shell

1. Go to your Render dashboard
2. Select your web service
3. Open the "Shell" tab (if available)
4. Run:
   ```bash
   python migrate_add_location.py
   ```

### Option 3: Add to Build Command

In your `render.yaml` or build settings, you could add:

```yaml
buildCommand: |
  pip install -r requirements.txt
  python migrate_add_location.py
```

**Note:** Be careful with this approach - it runs on every deploy. The migration script is safe (idempotent), but you may want to run it manually the first time.

## Troubleshooting

### Migration Fails with "Table doesn't exist"

If you see this error, you need to create the database tables first:

```bash
python init_db.py --init-only
```

Then run the migration again.

### Migration Fails with Permission Errors

Make sure your database user has `ALTER TABLE` permissions. For SQLite (local), this should work automatically. For PostgreSQL (Render), ensure your database user has the necessary permissions.

### Columns Already Exist

If you see errors about columns already existing, that's okay! The migration script checks for existence, but if you're seeing errors, you can safely ignore them or modify the script to use `IF NOT EXISTS` (though SQLite doesn't support this directly).

## Verification Checklist

After migration and deployment:

- [ ] Migration script runs without errors locally
- [ ] Can add events with location data via web UI
- [ ] Timeline events show location in details sidebar
- [ ] Clicking timeline event centers globe on location
- [ ] Map filter controls appear and work
- [ ] Location filtering works (events within radius)
- [ ] Clear filter button works
- [ ] Existing events still display correctly
- [ ] CSV import works with/without location columns
- [ ] All existing features (CRUD, search, etc.) still work

## Next Steps

After pushing to GitHub:

1. **Render will automatically deploy** (if auto-deploy is enabled)
2. **Run migration on Render** (see options above)
3. **Test the new features** on your production site
4. **Import location data** if you have CSV files with location columns

