# Fixing pandas Installation Error

## The Problem

You're getting an error because:
1. You're using Python 3.14.0 (very new)
2. pandas 2.1.3 doesn't have pre-built wheels for Python 3.14
3. It's trying to build from source but can't find C compiler tools

## Solution Options

### Option 1: Install Xcode Command Line Tools (Recommended for Local Dev)

This will allow pandas to build from source:

```bash
xcode-select --install
```

Then try installing again:
```bash
pip install -r requirements.txt
```

### Option 2: Use a Newer pandas Version (Easier)

I've updated `requirements.txt` to use `pandas>=2.2.0` which has better Python 3.14 support. Try:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Option 3: Use Python 3.11 or 3.12 (Most Compatible)

Since Render uses Python 3.11.9 (from `runtime.txt`), you might want to match that locally:

```bash
# Install Python 3.11 via Homebrew (if you have it)
brew install python@3.11

# Or use pyenv
pyenv install 3.11.9
pyenv local 3.11.9

# Recreate virtual environment
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Quick Fix (Try This First)

1. **Upgrade pip:**
   ```bash
   pip install --upgrade pip
   ```

2. **Install with updated requirements:**
   ```bash
   pip install -r requirements.txt
   ```

The updated `requirements.txt` uses `pandas>=2.2.0` which should have pre-built wheels for Python 3.14.

## If Still Having Issues

Install Xcode command line tools:
```bash
xcode-select --install
```

This will take a few minutes but will allow any package to build from source if needed.

## After Installation Works

Once dependencies are installed, continue with the migration:

```bash
# Set your Render database URL
export DATABASE_URL="postgres://user:password@host:port/dbname"

# Run migration
python migrate_add_location.py
```

