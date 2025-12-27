# Installation Instructions

## Fix: ModuleNotFoundError: No module named 'flask'

You need to install the required Python packages. Here are your options:

---

## Option 1: Using a Virtual Environment (RECOMMENDED)

This keeps your project dependencies separate from your system Python.

### Step 1: Create virtual environment
```bash
cd /Users/aschick/Documents/chronoverse
python3 -m venv venv
```

### Step 2: Activate the virtual environment
```bash
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the application
```bash
python run.py
```

**Note**: Every time you open a new terminal, you'll need to activate the virtual environment again:
```bash
cd /Users/aschick/Documents/chronoverse
source venv/bin/activate
python run.py
```

---

## Option 2: Install Globally (Simpler, but less isolated)

If you prefer not to use a virtual environment:

```bash
cd /Users/aschick/Documents/chronoverse
pip3 install Flask pandas plotly Werkzeug
```

Then run:
```bash
python3 run.py
```

---

## Option 3: Use the Setup Script

If the `setup.sh` script has execute permissions:

```bash
cd /Users/aschick/Documents/chronoverse
./setup.sh
source venv/bin/activate
python run.py
```

---

## Verify Installation

After installing, verify it worked:

```bash
python3 -c "import flask, pandas, plotly; print('✓ All packages installed successfully!')"
```

If you see the checkmark message, you're good to go!

---

## Troubleshooting

### "Permission denied" errors
Try using `sudo` (not recommended, but works):
```bash
sudo pip3 install Flask pandas plotly Werkzeug
```

### "pip3: command not found"
You may need to install pip first, or use `python3 -m pip` instead:
```bash
python3 -m pip install -r requirements.txt
```

### Still getting ModuleNotFoundError after installing
- Make sure you're using the same Python interpreter
- If using a virtual environment, make sure it's activated
- Try: `python3 -m pip install --user Flask pandas plotly Werkzeug`

---

## What Gets Installed

The `requirements.txt` file installs:
- **Flask** (3.0.0) - Web framework
- **pandas** (2.1.3) - Data processing
- **plotly** (5.18.0) - Interactive visualizations
- **Werkzeug** (3.0.1) - WSGI utilities (used by Flask)

