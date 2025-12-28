# Quick Migration Steps for Render Database

## Step 1: Activate Virtual Environment

```bash
cd /Users/aschick/Documents/repositories/TimeTrip
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

## Step 2: Install Dependencies (if not already installed)

```bash
pip install -r requirements.txt
```

This will install Flask, SQLAlchemy, and other required packages.

## Step 3: Set Render Database URL

Get your Render database URL from the Render dashboard, then:

```bash
export DATABASE_URL="postgres://user:password@host:port/dbname"
```

**Replace with your actual Render database URL!**

## Step 4: Run Migration

```bash
python migrate_add_location.py
```

You should see:
```
Checking database schema...
Adding 'lat' column...
  ✓ Added 'lat' column
...
Migration complete!
```

## Step 5: Verify (Optional)

You can verify by checking if you can import the app:

```bash
python -c "from app import create_app; app = create_app(); print('✓ App loads successfully')"
```

## Troubleshooting

### "No module named 'flask'" error
- Make sure you activated the virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### "Cannot connect to database" error
- Verify your `DATABASE_URL` is correct
- Make sure you're using the **External Database URL** from Render
- Check that your IP is allowed (Render may restrict external connections)

### "Table doesn't exist" error
- The table should already exist if your app is running on Render
- If not, you may need to run `db.create_all()` first (but this shouldn't be necessary)

