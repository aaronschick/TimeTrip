# Debugging Guide - No Data Showing in Chart

If your timeline chart is empty, follow these steps:

## Step 1: Test Data Loading

Run the test script to verify data is loading correctly:

```bash
python3 test_data.py
```

This will show:
- If the data file exists
- How many rows were loaded
- Sample data
- If figure generation works

## Step 2: Check the Browser Console

1. Open your browser's Developer Tools (F12 or Cmd+Option+I on Mac)
2. Go to the Console tab
3. Look for any JavaScript errors (shown in red)
4. Check the Network tab to see if `/api/timeline` is returning data

## Step 3: Test the API Directly

Open these URLs in your browser while the server is running:

1. **Debug endpoint** - Check if data is loading:
   ```
   http://localhost:5001/api/debug
   ```

2. **Data endpoint** - See raw data:
   ```
   http://localhost:5001/api/data?start_year=-5000000000&end_year=2025
   ```

3. **Timeline endpoint** - See the Plotly JSON:
   ```
   http://localhost:5001/api/timeline?start_year=-5000000000&end_year=2025
   ```

## Step 4: Common Issues

### Issue: "No data found" message
**Solution**: The year range might be too narrow. Try:
- Start year: `-5000000000`
- End year: `2025`

### Issue: Empty chart but data exists
**Possible causes**:
1. **Missing category data** - Some rows might have empty categories
2. **Year data issues** - Check if start_year/end_year are valid numbers
3. **JavaScript error** - Check browser console

### Issue: API returns error
**Check**:
1. Is the CSV file in the `data/` directory?
2. Does the file have the correct columns?
3. Check server logs for Python errors

## Step 5: Verify CSV Format

Your CSV should have these columns:
- `id`
- `title`
- `category` (required for plotting)
- `continent`
- `start_year` (required, must be numeric)
- `end_year` (required, must be numeric)
- `description`

Run this to check:
```bash
head -3 data/timeline_data.csv
```

## Step 6: Check Server Logs

When you run `python3 run.py`, watch the terminal output for any errors when you:
1. Load the page
2. Click "Update Timeline"
3. Make API requests

## Still Not Working?

If none of the above helps, check:
1. Are you using the correct port? (Should be 5001)
2. Is the Flask server actually running?
3. Try restarting the server
4. Clear your browser cache and reload

