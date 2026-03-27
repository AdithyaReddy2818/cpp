"""
Incident model for the Neighbourhood Safety Incident Reporting App.
Represents a safety incident reported by a resident.
Author: Adithya Reddy Madireddy
"""

from datetime import datetime, timezone
from models.database import db


class Incident(db.Model):
    """
    Incident entity representing a safety event reported in a neighbourhood.
    Each incident has a category, severity, geolocation, and lifecycle status
    that tracks its progression from initial report to resolution.
    """
    __tablename__ = 'incidents'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # theft, vandalism, suspicious_activity, etc.
    severity = db.Column(db.String(20), nullable=False, default='medium')  # critical, high, medium, low
    status = db.Column(db.String(30), nullable=False, default='reported')  # reported, investigating, resolved, closed
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    address = db.Column(db.String(300), nullable=True)
    neighbourhood_zone = db.Column(db.String(100), nullable=True)
    photo_urls = db.Column(db.Text, nullable=True)  # JSON array of S3 URLs stored as text
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_authority_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    comments = db.relationship('Comment', backref='incident', lazy=True,
                               cascade='all, delete-orphan')
    assigned_authority = db.relationship('User', foreign_keys=[assigned_authority_id])

    def to_dict(self):
        """Serialize the Incident object to a dictionary for JSON responses."""
        import json
        photo_list = []
        if self.photo_urls:
            try:
                photo_list = json.loads(self.photo_urls)
            except (json.JSONDecodeError, TypeError):
                photo_list = []

        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'severity': self.severity,
            'status': self.status,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'neighbourhood_zone': self.neighbourhood_zone,
            'photo_urls': photo_list,
            'reporter_id': self.reporter_id,
            'assigned_authority_id': self.assigned_authority_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Incident {self.title} [{self.status}]>'
