"""
Incident routes for full CRUD operations, photo upload, and status management.
Provides RESTful endpoints for creating, reading, updating, and deleting incidents.
Author: Adithya Reddy Madireddy
"""

import json
from flask import Blueprint, request, jsonify
from models.database import db
from models.incident import Incident
from models.user import User

incident_bp = Blueprint('incidents', __name__)


@incident_bp.route('/api/incidents', methods=['GET'])
def get_incidents():
    """Retrieve all incidents, with optional filtering by status, category, or severity."""
    try:
        query = Incident.query

        # Apply optional filters from query parameters
        status = request.args.get('status')
        if status:
            query = query.filter_by(status=status)

        category = request.args.get('category')
        if category:
            query = query.filter_by(category=category)

        severity = request.args.get('severity')
        if severity:
            query = query.filter_by(severity=severity)

        neighbourhood = request.args.get('neighbourhood')
        if neighbourhood:
            query = query.filter_by(neighbourhood_zone=neighbourhood)

        incidents = query.order_by(Incident.created_at.desc()).all()
        return jsonify([incident.to_dict() for incident in incidents]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@incident_bp.route('/api/incidents/<int:incident_id>', methods=['GET'])
def get_incident(incident_id):
    """Retrieve a single incident by its ID, including associated comments."""
    try:
        incident = Incident.query.get(incident_id)
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404
        result = incident.to_dict()
        result['comments'] = [c.to_dict() for c in incident.comments]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@incident_bp.route('/api/incidents', methods=['POST'])
def create_incident():
    """
    Create a new incident report. Requires title, description, category,
    and reporter_id. Optional fields include severity, location, photos.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        # Validate required fields
        required = ['title', 'description', 'category', 'reporter_id']
        for field in required:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Verify that the reporter exists
        reporter = User.query.get(data['reporter_id'])
        if not reporter:
            return jsonify({'error': 'Reporter not found'}), 404

        # Build the incident record
        incident = Incident(
            title=data['title'],
            description=data['description'],
            category=data['category'],
            severity=data.get('severity', 'medium'),
            status=data.get('status', 'reported'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            address=data.get('address'),
            neighbourhood_zone=data.get('neighbourhood_zone'),
            photo_urls=json.dumps(data.get('photo_urls', [])),
            reporter_id=data['reporter_id'],
            assigned_authority_id=data.get('assigned_authority_id')
        )

        db.session.add(incident)
        db.session.commit()

        return jsonify(incident.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@incident_bp.route('/api/incidents/<int:incident_id>', methods=['PUT'])
def update_incident(incident_id):
    """Update an existing incident with new data. Supports partial updates."""
    try:
        incident = Incident.query.get(incident_id)
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        # Update only the provided fields
        if 'title' in data:
            incident.title = data['title']
        if 'description' in data:
            incident.description = data['description']
        if 'category' in data:
            incident.category = data['category']
        if 'severity' in data:
            incident.severity = data['severity']
        if 'status' in data:
            incident.status = data['status']
        if 'latitude' in data:
            incident.latitude = data['latitude']
        if 'longitude' in data:
            incident.longitude = data['longitude']
        if 'address' in data:
            incident.address = data['address']
        if 'neighbourhood_zone' in data:
            incident.neighbourhood_zone = data['neighbourhood_zone']
        if 'photo_urls' in data:
            incident.photo_urls = json.dumps(data['photo_urls'])
        if 'assigned_authority_id' in data:
            incident.assigned_authority_id = data['assigned_authority_id']

        db.session.commit()
        return jsonify(incident.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@incident_bp.route('/api/incidents/<int:incident_id>', methods=['DELETE'])
def delete_incident(incident_id):
    """Delete an incident and all associated comments by its ID."""
    try:
        incident = Incident.query.get(incident_id)
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404

        db.session.delete(incident)
        db.session.commit()
        return jsonify({'message': 'Incident deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@incident_bp.route('/api/incidents/<int:incident_id>/status', methods=['PATCH'])
def update_incident_status(incident_id):
    """Update only the status of an incident. Used by authorities to progress incidents."""
    try:
        incident = Incident.query.get(incident_id)
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404

        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'error': 'status is required'}), 400

        valid_statuses = ['reported', 'investigating', 'resolved', 'closed']
        if data['status'] not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400

        incident.status = data['status']
        db.session.commit()
        return jsonify(incident.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@incident_bp.route('/api/incidents/<int:incident_id>/photos', methods=['POST'])
def upload_incident_photo(incident_id):
    """
    Upload a photo to an incident. Accepts a base64-encoded image or
    file upload via multipart form data. Stores in S3 and updates incident.
    """
    try:
        incident = Incident.query.get(incident_id)
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404

        # Handle the photo upload via JSON with base64 data
        data = request.get_json()
        if not data or 'photo_url' not in data:
            return jsonify({'error': 'photo_url is required'}), 400

        # Parse existing photo list and append the new URL
        existing_photos = []
        if incident.photo_urls:
            try:
                existing_photos = json.loads(incident.photo_urls)
            except (json.JSONDecodeError, TypeError):
                existing_photos = []

        existing_photos.append(data['photo_url'])
        incident.photo_urls = json.dumps(existing_photos)
        db.session.commit()

        return jsonify(incident.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@incident_bp.route('/api/incidents/stats', methods=['GET'])
def get_incident_stats():
    """Return aggregate statistics about incidents for the dashboard."""
    try:
        total = Incident.query.count()
        reported = Incident.query.filter_by(status='reported').count()
        investigating = Incident.query.filter_by(status='investigating').count()
        resolved = Incident.query.filter_by(status='resolved').count()
        closed = Incident.query.filter_by(status='closed').count()

        # Category breakdown
        categories = db.session.query(
            Incident.category, db.func.count(Incident.id)
        ).group_by(Incident.category).all()

        # Severity breakdown
        severities = db.session.query(
            Incident.severity, db.func.count(Incident.id)
        ).group_by(Incident.severity).all()

        return jsonify({
            'total': total,
            'by_status': {
                'reported': reported,
                'investigating': investigating,
                'resolved': resolved,
                'closed': closed
            },
            'by_category': {cat: count for cat, count in categories},
            'by_severity': {sev: count for sev, count in severities}
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
