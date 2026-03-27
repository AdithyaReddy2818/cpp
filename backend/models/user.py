"""
User model for the Neighbourhood Safety Incident Reporting App.
Represents residents, authorities, and administrators in the system.
Author: Adithya Reddy Madireddy
"""

from datetime import datetime, timezone
from models.database import db


class User(db.Model):
    """
    User entity representing a person registered in the safety reporting system.
    Users can be residents who report incidents, authorities who manage them,
    or administrators who oversee the entire system.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(300), nullable=True)
    neighbourhood = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='resident')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    incidents = db.relationship('Incident', backref='reporter', lazy=True,
                                foreign_keys='Incident.reporter_id')
    comments = db.relationship('Comment', backref='author', lazy=True)

    def to_dict(self):
        """Serialize the User object to a dictionary for JSON responses."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'neighbourhood': self.neighbourhood,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<User {self.name} ({self.role})>'
