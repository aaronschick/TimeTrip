"""
Database models for TimeTrip application
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class TimelineEvent(db.Model):
    """Model representing a timeline event"""
    __tablename__ = 'timeline_events'
    
    id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    continent = db.Column(db.String(100), default='Global')
    start_year = db.Column(db.BigInteger, nullable=False)
    end_year = db.Column(db.BigInteger, nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'continent': self.continent,
            'start_year': self.start_year,
            'end_year': self.end_year,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
        }
    
    def __repr__(self):
        return f'<TimelineEvent {self.id}: {self.title}>'

