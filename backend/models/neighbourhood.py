"""
Neighbourhood model for the Neighbourhood Safety Incident Reporting App.
Represents a geographical zone within the community.
Author: Adithya Reddy Madireddy
"""

from datetime import datetime, timezone
from models.database import db


class Neighbourhood(db.Model):
    """
    Neighbourhood entity representing a defined geographic zone in the community.
    Each neighbourhood has boundaries and an assigned authority contact for
    incident escalation and management.
    """
    __tablename__ = 'neighbourhoods'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    zone_code = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    boundaries = db.Column(db.Text, nullable=True)  # JSON polygon coordinates
    contact_authority = db.Column(db.String(150), nullable=True)
    contact_email = db.Column(db.String(200), nullable=True)
    contact_phone = db.Column(db.String(20), nullable=True)
    population = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Serialize the Neighbourhood object to a dictionary for JSON responses."""
        import json
        boundary_data = None
        if self.boundaries:
            try:
                boundary_data = json.loads(self.boundaries)
            except (json.JSONDecodeError, TypeError):
                boundary_data = None

        return {
            'id': self.id,
            'name': self.name,
            'zone_code': self.zone_code,
            'description': self.description,
            'boundaries': boundary_data,
            'contact_authority': self.contact_authority,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'population': self.population,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Neighbourhood {self.name} ({self.zone_code})>'
