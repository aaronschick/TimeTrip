# Chronoverse - Universal Timeline

A web application for visualizing a universal timeline spanning Earth history, world events, and space history.

## Features

- **Interactive Timeline Visualization**: Dual-view timeline showing both numeric years (for deep time) and calendar dates (for recent history)
- **Multiple Categories**: Visualize events by category (era, migration, civilization, empire, war, religion, biblical)
- **Customizable Time Range**: Adjust start and end years to explore different periods
- **Modern UI**: Beautiful, responsive interface with dark theme
- **Interactive Plotly Charts**: Pan, zoom, and hover to explore events

## Project Structure

```
chronoverse/
├── app/                    # Flask application
│   ├── __init__.py        # App factory
│   ├── routes.py          # Route handlers
│   └── timeline.py        # Timeline generation logic
├── static/                # Static files
│   ├── css/
│   │   └── style.css     # Stylesheet
│   └── js/
│       └── main.js        # Frontend JavaScript
├── templates/             # HTML templates
│   └── index.html         # Main page
├── data/                  # Data files
│   └── timeline_data.csv  # Timeline event data
├── config.py             # Configuration settings
├── run.py                 # Application entry point
├── requirements.txt       # Python dependencies
├── chronoverse_v1.ipynb   # Original proof of concept notebook
└── README.md             # This file
```

**Note**: The original proof of concept was developed in `chronoverse_v1.ipynb`. The web application preserves all the functionality while providing a more scalable structure.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or using a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python run.py
```

The application will be available at `http://localhost:5001`

**Note**: The default port is 5001 to avoid conflicts with macOS AirPlay Receiver (which uses port 5000). You can change this by setting the `PORT` environment variable or editing `config.py`.

### 3. Development Mode

The application runs in debug mode by default. For production, set environment variables:

```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
```

## Data Format

The timeline data is stored in CSV format with the following columns:

- `id`: Unique identifier
- `title`: Event title
- `category`: Event category (era, migration, civilization, empire, war, religion, biblical)
- `continent`: Geographic region
- `start_year`: Start year (negative for BCE)
- `end_year`: End year
- `description`: Event description
- `start_date` (optional): Precise start date for recent events
- `end_date` (optional): Precise end date for recent events

## API Endpoints

- `GET /`: Main timeline page
- `GET /api/timeline?start_year=<int>&end_year=<int>`: Get timeline visualization data
- `GET /api/data?start_year=<int>&end_year=<int>`: Get raw timeline data as JSON

## Future Enhancements

Potential improvements for the application:

- [ ] Add filtering by category, continent, or other attributes
- [ ] Search functionality for events
- [ ] Event detail modal/popup
- [ ] Export timeline as image or PDF
- [ ] User authentication for adding/editing events
- [ ] Database backend (SQLite/PostgreSQL) instead of CSV
- [ ] Admin panel for data management
- [ ] Multiple timeline views (vertical, horizontal, Gantt-style)
- [ ] Timeline comparison mode
- [ ] Integration with external historical databases

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Data Processing**: Pandas
- **Visualization**: Plotly
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Data Format**: CSV

## License

This project is open source and available for personal and educational use.

