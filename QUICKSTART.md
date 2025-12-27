# Quick Start Guide

## Step 1: Install Dependencies

You have two options:

### Option A: Install directly (simplest)
```bash
pip3 install -r requirements.txt
```

### Option B: Use a virtual environment (recommended)
```bash
# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Run the Application

Simply run:
```bash
python3 run.py
```

Or if you're using a virtual environment:
```bash
python run.py
```

## Step 3: Open in Browser

Once you see output like:
```
 * Running on http://127.0.0.1:5000
```

Open your web browser and go to:
**http://localhost:5000**

## Troubleshooting

### If you get "ModuleNotFoundError"
Make sure you've installed all dependencies:
```bash
pip3 install Flask pandas plotly Werkzeug
```

### If port 5000 is already in use
Edit `run.py` and change the port:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### If you get import errors
Make sure you're running from the project root directory:
```bash
cd /Users/aschick/Documents/chronoverse
python3 run.py
```

## Stopping the Server

Press `Ctrl+C` in the terminal to stop the server.

