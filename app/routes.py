from flask import Blueprint, render_template, jsonify, request
import os
import sys
import pandas as pd

# Import config - handle both direct execution and Flask app context
try:
    from config import Config
except ImportError:
    # If running as module, add parent to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import Config

from app.timeline import TimelineGenerator

bp = Blueprint('main', __name__)

# Initialize timeline generator
timeline_gen = TimelineGenerator(Config.TIMELINE_DATA_FILE)

@bp.route('/')
def index():
    """Main timeline page"""
    return render_template('index.html')

@bp.route('/api/timeline')
def get_timeline():
    """API endpoint to generate timeline figure"""
    start_year = request.args.get('start_year', type=int, default=-5_000_000_000)
    end_year = request.args.get('end_year', type=int, default=2025)
    
    try:
        # Get count before generating figure
        filtered_data = timeline_gen.get_filtered_data(start_year, end_year)
        event_count = len(filtered_data)
        
        fig_json = timeline_gen.make_figure_json(start_year, end_year)
        
        # Add metadata about event count
        if 'layout' not in fig_json:
            fig_json['layout'] = {}
        if 'annotations' not in fig_json['layout']:
            fig_json['layout']['annotations'] = []
        
        # Add annotation showing event count (will be added to layout)
        fig_json['_metadata'] = {
            'total_events': len(timeline_gen.df),
            'filtered_events': event_count,
            'start_year': start_year,
            'end_year': end_year
        }
        
        return jsonify(fig_json)
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@bp.route('/api/data')
def get_data():
    """API endpoint to get raw timeline data"""
    start_year = request.args.get('start_year', type=int, default=-5_000_000_000)
    end_year = request.args.get('end_year', type=int, default=2025)
    
    try:
        data = timeline_gen.get_filtered_data(start_year, end_year)
        # Convert to dict, handling NaN values
        records = data.replace({pd.NA: None, pd.NaT: None}).to_dict('records')
        return jsonify({
            'count': len(records),
            'data': records
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@bp.route('/api/debug')
def debug():
    """Debug endpoint to check data loading"""
    try:
        total_rows = len(timeline_gen.df)
        
        # Convert sample data, handling NaT and NaN values
        sample_df = timeline_gen.df.head(5).copy()
        sample_data = sample_df.replace({pd.NA: None, pd.NaT: None}).to_dict('records')
        # Convert any remaining datetime/NaT to strings
        for record in sample_data:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
                elif hasattr(value, 'isoformat'):  # datetime objects
                    record[key] = value.isoformat()
        
        columns = list(timeline_gen.df.columns)
        
        # Check filtered data for default range
        default_start = -5_000_000_000
        default_end = 2025
        filtered = timeline_gen.get_filtered_data(default_start, default_end)
        
        # Check for missing data
        missing_years = timeline_gen.df['year'].isna().sum()
        missing_categories = timeline_gen.df['category'].isna().sum() if 'category' in timeline_gen.df.columns else 0
        
        return jsonify({
            'total_rows': total_rows,
            'filtered_rows': len(filtered),
            'missing_years': int(missing_years),
            'missing_categories': int(missing_categories),
            'columns': columns,
            'sample': sample_data,
            'data_file': Config.TIMELINE_DATA_FILE,
            'file_exists': os.path.exists(Config.TIMELINE_DATA_FILE),
            'year_range': {
                'min': float(timeline_gen.df['start_year'].min()),
                'max': float(timeline_gen.df['end_year'].max())
            },
            'categories': timeline_gen.df['category'].value_counts().to_dict() if 'category' in timeline_gen.df.columns else {}
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

