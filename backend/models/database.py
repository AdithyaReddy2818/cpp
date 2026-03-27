"""
Database initialization module.
Creates and configures the SQLAlchemy database instance used across the application.
Author: Adithya Reddy Madireddy
"""

from flask_sqlalchemy import SQLAlchemy

# Global SQLAlchemy instance shared by all models
db = SQLAlchemy()


def init_db(app):
    """
    Initialize the database with the given Flask application.
    Creates all tables if they do not already exist.

    Args:
        app: The Flask application instance.
    """
    db.init_app(app)
    with app.app_context():
        db.create_all()
