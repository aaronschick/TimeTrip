from flask import Blueprint, render_template, jsonify, request, current_app
import os
import sys
import pandas as pd
import uuid
from datetime import datetime

# Import config - handle both direct execution and Flask app context
try:
    from config import Config
except ImportError:
    # If running as module, add parent to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import Config

from app.timeline import TimelineGenerator
from app.models import db, TimelineEvent
from sqlalchemy import text

bp = Blueprint('main', __name__)

def get_timeline_generator():
    """Get timeline generator with current database session"""
    return TimelineGenerator(db.session)

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
        timeline_gen = get_timeline_generator()
        
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
        timeline_gen = get_timeline_generator()
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
        timeline_gen = get_timeline_generator()
        total_rows = len(timeline_gen.df)
        
        # Convert sample data, handling NaT and NaN values
        sample_df = timeline_gen.df.head(5).copy() if not timeline_gen.df.empty else pd.DataFrame()
        sample_data = sample_df.replace({pd.NA: None, pd.NaT: None}).to_dict('records') if not sample_df.empty else []
        # Convert any remaining datetime/NaT to strings
        for record in sample_data:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
                elif hasattr(value, 'isoformat'):  # datetime objects
                    record[key] = value.isoformat()
        
        columns = list(timeline_gen.df.columns) if not timeline_gen.df.empty else []
        
        # Check filtered data for default range
        default_start = -5_000_000_000
        default_end = 2025
        filtered = timeline_gen.get_filtered_data(default_start, default_end)
        
        # Check for missing data
        missing_years = timeline_gen.df['year'].isna().sum() if not timeline_gen.df.empty and 'year' in timeline_gen.df.columns else 0
        missing_categories = timeline_gen.df['category'].isna().sum() if not timeline_gen.df.empty and 'category' in timeline_gen.df.columns else 0
        
        # Database info
        db_count = TimelineEvent.query.count()
        
        # Check if dataframe has valid year data
        valid_year_data = 0
        if not timeline_gen.df.empty and 'start_year' in timeline_gen.df.columns and 'end_year' in timeline_gen.df.columns:
            valid_year_data = len(timeline_gen.df[
                (timeline_gen.df['start_year'].notna()) & 
                (timeline_gen.df['end_year'].notna())
            ])
        
        # Test figure generation
        try:
            test_fig = timeline_gen.make_figure_json(default_start, default_end)
            figure_has_data = test_fig.get('data') and len(test_fig.get('data', [])) > 0
        except Exception as fig_error:
            figure_has_data = False
            figure_error_msg = str(fig_error)
        
        return jsonify({
            'total_rows': total_rows,
            'db_count': db_count,
            'valid_year_data': valid_year_data,
            'filtered_rows': len(filtered),
            'missing_years': int(missing_years),
            'missing_categories': int(missing_categories),
            'columns': columns,
            'sample': sample_data,
            'database_url': Config.SQLALCHEMY_DATABASE_URI.split('@')[-1] if '@' in Config.SQLALCHEMY_DATABASE_URI else 'sqlite',
            'year_range': {
                'min': float(timeline_gen.df['start_year'].min()) if not timeline_gen.df.empty and 'start_year' in timeline_gen.df.columns and timeline_gen.df['start_year'].notna().any() else None,
                'max': float(timeline_gen.df['end_year'].max()) if not timeline_gen.df.empty and 'end_year' in timeline_gen.df.columns and timeline_gen.df['end_year'].notna().any() else None
            },
            'categories': timeline_gen.df['category'].value_counts().to_dict() if 'category' in timeline_gen.df.columns and not timeline_gen.df.empty else {},
            'figure_generation': {
                'success': figure_has_data if 'figure_has_data' in locals() else False,
                'error': figure_error_msg if 'figure_error_msg' in locals() else None
            }
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@bp.route('/api/events', methods=['POST'])
def add_event():
    """Add a new event to the timeline"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'category', 'start_year']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate ID if not provided
        event_id = data.get('id') or f"event-{uuid.uuid4().hex[:8]}"
        
        # Check if ID already exists
        existing = TimelineEvent.query.filter_by(id=event_id).first()
        if existing:
            return jsonify({'error': f'Event with ID "{event_id}" already exists'}), 400
        
        # Parse dates if provided
        start_date = None
        end_date = None
        
        if data.get('start_date'):
            try:
                start_date = pd.to_datetime(data['start_date'], errors='coerce')
                if pd.notna(start_date):
                    start_date = start_date.date()
                else:
                    start_date = None
            except:
                start_date = None
        
        if data.get('end_date'):
            try:
                end_date = pd.to_datetime(data['end_date'], errors='coerce')
                if pd.notna(end_date):
                    end_date = end_date.date()
                else:
                    end_date = None
            except:
                end_date = None
        
        # Create new event
        new_event = TimelineEvent(
            id=event_id,
            title=data['title'].strip(),
            category=data['category'].strip(),
            continent=data.get('continent', 'Global').strip(),
            start_year=int(data['start_year']),
            end_year=int(data.get('end_year', data['start_year'])),
            description=data.get('description', '').strip() or None,
            start_date=start_date,
            end_date=end_date
        )
        
        # Add to database
        db.session.add(new_event)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Event added successfully',
            'event': new_event.to_dict()
        }), 201
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@bp.route('/api/events/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete an event from the timeline"""
    try:
        # Check if event exists
        event = TimelineEvent.query.filter_by(id=event_id).first()
        if not event:
            return jsonify({'error': f'Event with ID "{event_id}" not found'}), 404
        
        # Delete event
        db.session.delete(event)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Event "{event_id}" deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@bp.route('/api/events', methods=['GET'])
def list_events():
    """Get list of all events (for management)"""
    try:
        start_year = request.args.get('start_year', type=int)
        end_year = request.args.get('end_year', type=int)
        
        # Check database connection
        try:
            db.session.execute(text('SELECT 1'))
        except Exception as db_error:
            return jsonify({
                'error': 'Database connection failed',
                'message': str(db_error),
                'hint': 'Please ensure DATABASE_URL is set correctly and the database is accessible.'
            }), 503
        
        # Query database
        query = TimelineEvent.query
        
        # Apply year filters if provided
        if start_year is not None:
            query = query.filter(TimelineEvent.end_year >= start_year)
        if end_year is not None:
            query = query.filter(TimelineEvent.start_year <= end_year)
        
        events = query.all()
        
        # Convert to dict
        records = [event.to_dict() for event in events]
        
        return jsonify({
            'count': len(records),
            'data': records
        })
    except Exception as e:
        import traceback
        db.session.rollback()
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@bp.route('/api/import-csv', methods=['POST'])
def import_csv():
    """Import events from CSV file into database"""
    try:
        from config import Config
        import pandas as pd
        from datetime import datetime
        
        csv_path = Config.TIMELINE_DATA_FILE
        
        # Check if file exists
        if not os.path.exists(csv_path):
            return jsonify({
                'error': f'CSV file not found at {csv_path}',
                'hint': 'Make sure timeline_data_4.csv is in the repository root'
            }), 404
        
        # Check if data already exists
        existing_count = TimelineEvent.query.count()
        if existing_count > 0:
            # Check if user wants to overwrite (for web interface, we'll append by default)
            # Or we can clear first - let's make it optional via query param
            clear_existing = request.args.get('clear', 'false').lower() == 'true'
            if clear_existing:
                TimelineEvent.query.delete()
                db.session.commit()
        
        # Read CSV
        df = pd.read_csv(csv_path)
        df = df.dropna(axis=1, how='all')  # Remove empty columns
        
        imported = 0
        skipped = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # Skip rows with missing required fields
                if pd.isna(row.get('id')) or pd.isna(row.get('title')) or pd.isna(row.get('start_year')):
                    skipped += 1
                    continue
                
                # Check if event already exists
                event_id = str(row['id']).strip()
                existing = TimelineEvent.query.filter_by(id=event_id).first()
                if existing:
                    skipped += 1
                    continue
                
                # Parse dates
                start_date = None
                end_date = None
                
                if 'start_date' in row and pd.notna(row['start_date']):
                    try:
                        start_date = pd.to_datetime(row['start_date'], errors='coerce')
                        if pd.notna(start_date):
                            start_date = start_date.date()
                        else:
                            start_date = None
                    except:
                        start_date = None
                
                if 'end_date' in row and pd.notna(row['end_date']):
                    try:
                        end_date = pd.to_datetime(row['end_date'], errors='coerce')
                        if pd.notna(end_date):
                            end_date = end_date.date()
                        else:
                            end_date = None
                    except:
                        end_date = None
                
                # Create event
                event = TimelineEvent(
                    id=event_id,
                    title=str(row['title']).strip(),
                    category=str(row.get('category', 'other')).strip(),
                    continent=str(row.get('continent', 'Global')).strip(),
                    start_year=int(row['start_year']),
                    end_year=int(row.get('end_year', row['start_year'])),
                    description=str(row.get('description', '')).strip() if pd.notna(row.get('description')) else None,
                    start_date=start_date,
                    end_date=end_date
                )
                
                db.session.add(event)
                imported += 1
                
                # Commit in batches
                if imported % 50 == 0:
                    db.session.commit()
                    
            except Exception as e:
                errors.append(f"Row {idx + 2} (ID: {row.get('id', 'unknown')}): {str(e)}")
                skipped += 1
                continue
        
        # Final commit
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'CSV import completed',
            'imported': imported,
            'skipped': skipped,
            'errors': errors[:10] if errors else [],  # Limit errors shown
            'total_errors': len(errors)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@bp.route('/api/import-status', methods=['GET'])
def import_status():
    """Check import status - how many events are in the database"""
    try:
        total_events = TimelineEvent.query.count()
        from config import Config
        csv_exists = os.path.exists(Config.TIMELINE_DATA_FILE)
        
        return jsonify({
            'total_events': total_events,
            'csv_file_exists': csv_exists,
            'csv_file_path': Config.TIMELINE_DATA_FILE if csv_exists else None,
            'database_connected': True
        })
    except Exception as e:
        return jsonify({
            'total_events': 0,
            'error': str(e),
            'database_connected': False
        }), 500

