"""
Neighbourhood routes for full CRUD operations on neighbourhood zones.
Manages geographic zones and their authority contacts.
Author: Adithya Reddy Madireddy
"""

import json
from flask import Blueprint, request, jsonify
from models.database import db
from models.neighbourhood import Neighbourhood

neighbourhood_bp = Blueprint('neighbourhoods', __name__)


@neighbourhood_bp.route('/api/neighbourhoods', methods=['GET'])
def get_neighbourhoods():
    """Retrieve all neighbourhoods."""
    try:
        neighbourhoods = Neighbourhood.query.order_by(Neighbourhood.name).all()
        return jsonify([n.to_dict() for n in neighbourhoods]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@neighbourhood_bp.route('/api/neighbourhoods/<int:neighbourhood_id>', methods=['GET'])
def get_neighbourhood(neighbourhood_id):
    """Retrieve a single neighbourhood by its ID."""
    try:
        neighbourhood = Neighbourhood.query.get(neighbourhood_id)
        if not neighbourhood:
            return jsonify({'error': 'Neighbourhood not found'}), 404
        return jsonify(neighbourhood.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@neighbourhood_bp.route('/api/neighbourhoods', methods=['POST'])
def create_neighbourhood():
    """
    Create a new neighbourhood zone. Requires name and zone_code.
    Boundaries are stored as a JSON string of polygon coordinates.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        if 'name' not in data:
            return jsonify({'error': 'name is required'}), 400
        if 'zone_code' not in data:
            return jsonify({'error': 'zone_code is required'}), 400

        # Check for duplicate zone code
        existing = Neighbourhood.query.filter_by(zone_code=data['zone_code']).first()
        if existing:
            return jsonify({'error': 'Zone code already exists'}), 409

        boundaries = data.get('boundaries')
        if boundaries and isinstance(boundaries, (list, dict)):
            boundaries = json.dumps(boundaries)

        neighbourhood = Neighbourhood(
            name=data['name'],
            zone_code=data['zone_code'],
            description=data.get('description'),
            boundaries=boundaries,
            contact_authority=data.get('contact_authority'),
            contact_email=data.get('contact_email'),
            contact_phone=data.get('contact_phone'),
            population=data.get('population')
        )

        db.session.add(neighbourhood)
        db.session.commit()
        return jsonify(neighbourhood.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@neighbourhood_bp.route('/api/neighbourhoods/<int:neighbourhood_id>', methods=['PUT'])
def update_neighbourhood(neighbourhood_id):
    """Update an existing neighbourhood. Supports partial updates."""
    try:
        neighbourhood = Neighbourhood.query.get(neighbourhood_id)
        if not neighbourhood:
            return jsonify({'error': 'Neighbourhood not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        if 'name' in data:
            neighbourhood.name = data['name']
        if 'zone_code' in data:
            if data['zone_code'] != neighbourhood.zone_code:
                existing = Neighbourhood.query.filter_by(zone_code=data['zone_code']).first()
                if existing:
                    return jsonify({'error': 'Zone code already exists'}), 409
            neighbourhood.zone_code = data['zone_code']
        if 'description' in data:
            neighbourhood.description = data['description']
        if 'boundaries' in data:
            boundaries = data['boundaries']
            if isinstance(boundaries, (list, dict)):
                boundaries = json.dumps(boundaries)
            neighbourhood.boundaries = boundaries
        if 'contact_authority' in data:
            neighbourhood.contact_authority = data['contact_authority']
        if 'contact_email' in data:
            neighbourhood.contact_email = data['contact_email']
        if 'contact_phone' in data:
            neighbourhood.contact_phone = data['contact_phone']
        if 'population' in data:
            neighbourhood.population = data['population']

        db.session.commit()
        return jsonify(neighbourhood.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@neighbourhood_bp.route('/api/neighbourhoods/<int:neighbourhood_id>', methods=['DELETE'])
def delete_neighbourhood(neighbourhood_id):
    """Delete a neighbourhood zone by its ID."""
    try:
        neighbourhood = Neighbourhood.query.get(neighbourhood_id)
        if not neighbourhood:
            return jsonify({'error': 'Neighbourhood not found'}), 404

        db.session.delete(neighbourhood)
        db.session.commit()
        return jsonify({'message': 'Neighbourhood deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@neighbourhood_bp.route('/api/neighbourhoods/stats', methods=['GET'])
def get_neighbourhood_stats():
    """Return aggregate statistics about neighbourhoods."""
    try:
        total = Neighbourhood.query.count()
        total_population = db.session.query(
            db.func.sum(Neighbourhood.population)
        ).scalar() or 0

        return jsonify({
            'total_neighbourhoods': total,
            'total_population': total_population
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
