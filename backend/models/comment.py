"""
Comment model for the Neighbourhood Safety Incident Reporting App.
Represents updates and comments attached to incidents.
Author: Adithya Reddy Madireddy
"""

from datetime import datetime, timezone
from models.database import db


class Comment(db.Model):
    """
    Comment entity representing a text update or note on an incident.
    Both residents and authorities can post comments to track incident progress.
    """
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text, nullable=False)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Serialize the Comment object to a dictionary for JSON responses."""
        return {
            'id': self.id,
            'text': self.text,
            'incident_id': self.incident_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Comment {self.id} on Incident {self.incident_id}>'
