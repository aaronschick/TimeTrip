# How to Run Chronoverse

## Quick Start (3 Steps)

### 1. Install Dependencies

**Option A: Using the setup script (easiest)**
```bash
./setup.sh
source venv/bin/activate
```

**Option B: Manual installation**
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

**Option C: Install globally (not recommended)**
```bash
pip3 install -r requirements.txt
```

### 2. Run the Application

```bash
python3 run.py
```

You should see output like:
```
 * Running on http://127.0.0.1:5000
 * Running on http://0.0.0.0:5000
```

### 3. Open in Your Browser

Navigate to: **http://localhost:5001**

**Note**: The default port is 5001 (instead of 5000) to avoid conflicts with macOS AirPlay Receiver.

You should see the Chronoverse timeline interface!

---

## Detailed Explanation

### What Happens When You Run `python3 run.py`?

1. **`run.py`** is the entry point - it imports and creates the Flask app
2. **Flask starts a web server** on port 5000
3. **The app loads your timeline data** from `data/timeline_data.csv`
4. **When you visit the page**, Flask serves the HTML template
5. **JavaScript makes API calls** to `/api/timeline` to get the visualization data
6. **Plotly renders** the interactive timeline chart

### Project Flow

```
Browser Request
    ↓
Flask Routes (routes.py)
    ↓
Timeline Generator (timeline.py)
    ↓
CSV Data (data/timeline_data.csv)
    ↓
Plotly Visualization
    ↓
JSON Response
    ↓
Frontend JavaScript (main.js)
    ↓
Plotly Renders Chart
```

### File Structure Overview

- **`run.py`** - Starts the Flask server
- **`app/routes.py`** - Handles web requests (homepage, API endpoints)
- **`app/timeline.py`** - Generates the Plotly visualizations
- **`templates/index.html`** - The webpage you see in the browser
- **`static/js/main.js`** - Frontend code that updates the timeline
- **`static/css/style.css`** - Styling for the webpage
- **`data/timeline_data.csv`** - Your timeline event data

---

## Common Commands

### Start the server
```bash
python3 run.py
```

### Stop the server
Press `Ctrl+C` in the terminal

### Check if dependencies are installed
```bash
python3 -c "import flask, pandas, plotly; print('All good!')"
```

### View what's running on port 5000
```bash
lsof -i :5000
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
**Solution**: Install dependencies:
```bash
pip3 install -r requirements.txt
```

### "Address already in use"
**Solution**: The default port is already set to 5001 to avoid macOS AirPlay conflicts. If 5001 is also in use:
- Change the port in `config.py` (set `PORT = 8080` or another port), or
- Set environment variable: `export PORT=8080` before running

### "FileNotFoundError: timeline_data.csv"
**Solution**: Make sure you're running from the project root directory:
```bash
cd /Users/aschick/Documents/chronoverse
python3 run.py
```

### Virtual environment not activating
**Solution**: Make sure you're in the project directory and the venv exists:
```bash
cd /Users/aschick/Documents/chronoverse
source venv/bin/activate
```

### Browser shows "This site can't be reached"
**Solution**: 
1. Make sure the server is running (check terminal for "Running on...")
2. Try `http://127.0.0.1:5000` instead of `localhost:5000`
3. Check your firewall settings

---

## Development Mode

The app runs in **debug mode** by default, which means:
- ✅ Automatic reloading when you change code
- ✅ Detailed error messages
- ⚠️ Not suitable for production

To run in production mode, edit `run.py`:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

---

## Next Steps

Once it's running, you can:
- Adjust the time range using the controls
- Explore different historical periods
- Modify the code to add new features
- Add more events to `data/timeline_data.csv`

