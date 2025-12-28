# Running Migration on Render Database

Since your database is hosted on Render, you need to run the migration against the Render PostgreSQL database. Here are your options:

## Option 1: Run Migration Locally (Pointing to Render DB) - RECOMMENDED

This is the easiest method - run the migration script on your local machine but connect it to Render's database.

### Step 1: Get Your Render Database URL

1. Go to your Render dashboard: https://dashboard.render.com
2. Navigate to your **PostgreSQL database** (not the web service)
3. Go to the **"Info"** tab
4. Copy the **"Internal Database URL"** or **"External Database URL"**
   - Format: `postgres://user:password@host:port/dbname`

### Step 2: Set Environment Variable Locally

**On macOS/Linux:**
```bash
export DATABASE_URL="postgres://user:password@host:port/dbname"
```

**Or create a `.env` file** (don't commit this!):
```bash
# .env file
DATABASE_URL=postgres://user:password@host:port/dbname
```

Then load it:
```bash
source .env  # or use a tool like python-dotenv
```

### Step 3: Run Migration

```bash
cd /Users/aschick/Documents/repositories/TimeTrip
python migrate_add_location.py
```

The script will use the `DATABASE_URL` environment variable to connect to Render's database.

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

## Option 2: Run Migration via Render Shell

If Render provides shell access to your web service:

### Step 1: Access Render Shell

1. Go to your Render dashboard
2. Select your **Web Service** (not the database)
3. Look for a **"Shell"** tab or **"Console"** option
4. Open it

### Step 2: Run Migration

In the Render shell:
```bash
cd /opt/render/project/src  # or wherever your code is
python migrate_add_location.py
```

**Note:** The `DATABASE_URL` environment variable should already be set in Render, so the script will automatically connect to your Render database.

## Option 3: Add Migration to Build/Deploy Process

You can modify your deployment to run the migration automatically. However, be careful - you only want to run it once (or make sure it's idempotent, which our script is).

### Update `render.yaml`:

```yaml
services:
  - type: web
    name: timetrip
    env: python
    buildCommand: |
      pip install -r requirements.txt
      python migrate_add_location.py
    startCommand: gunicorn run:app --bind 0.0.0.0:$PORT
    envVars:
      - key: PORT
        value: 10000
```

**Warning:** This runs on every deploy. Our migration script is safe (idempotent), but you may want to run it manually the first time.

## Option 4: Use Render's Database Console (psql)

If Render provides direct database access:

1. Go to your PostgreSQL database in Render dashboard
2. Look for **"Connect"** or **"psql"** option
3. Connect and run SQL directly:

```sql
-- Check if columns exist first
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'timeline_events';

-- Add columns if they don't exist
ALTER TABLE timeline_events ADD COLUMN IF NOT EXISTS lat FLOAT;
ALTER TABLE timeline_events ADD COLUMN IF NOT EXISTS lon FLOAT;
ALTER TABLE timeline_events ADD COLUMN IF NOT EXISTS location_label VARCHAR(500);
ALTER TABLE timeline_events ADD COLUMN IF NOT EXISTS geometry TEXT;
ALTER TABLE timeline_events ADD COLUMN IF NOT EXISTS location_confidence VARCHAR(20) DEFAULT 'exact';
```

## Recommended Approach

**I recommend Option 1** (run locally pointing to Render DB) because:
- ✅ Easiest to set up
- ✅ You can see the output clearly
- ✅ No need to modify deployment configs
- ✅ Safe and reversible

## Security Note

⚠️ **Important:** Never commit your `.env` file or database credentials to git!

Make sure `.env` is in your `.gitignore`:
```
.env
*.env
```

## Verification

After running the migration, verify it worked:

1. **Check via your app:**
   - Deploy your code changes
   - Try adding an event with location data
   - If it works, the migration succeeded!

2. **Check via SQL (if you have access):**
   ```sql
   \d timeline_events  -- In psql
   -- or
   SELECT column_name, data_type 
   FROM information_schema.columns 
   WHERE table_name = 'timeline_events';
   ```

You should see the new columns: `lat`, `lon`, `location_label`, `geometry`, `location_confidence`

## Troubleshooting

### "Connection refused" or "Cannot connect to database"

- Make sure you're using the **External Database URL** (not Internal) if running locally
- Check that your IP is allowed (Render may restrict external connections)
- Verify the `DATABASE_URL` format is correct

### "Permission denied" or "ALTER TABLE" errors

- Ensure your database user has `ALTER TABLE` permissions
- You may need to use the database owner account

### Migration runs but columns don't appear

- Check you're looking at the correct database
- Verify the table name is `timeline_events` (case-sensitive in some databases)
- Try running the migration again (it's safe - it checks for existing columns)

## Next Steps After Migration

1. ✅ Migration complete
2. ✅ Push code changes to GitHub
3. ✅ Render auto-deploys (or manually deploy)
4. ✅ Test adding events with location data
5. ✅ Test timeline → globe linking
6. ✅ Test globe → timeline filtering

