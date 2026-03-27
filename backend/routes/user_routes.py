"""
User routes for full CRUD operations on user accounts.
Supports residents, authorities, and admin role management.
Author: Adithya Reddy Madireddy
"""

from flask import Blueprint, request, jsonify
from models.database import db
from models.user import User

user_bp = Blueprint('users', __name__)


@user_bp.route('/api/users', methods=['GET'])
def get_users():
    """Retrieve all users, with optional filtering by role or neighbourhood."""
    try:
        query = User.query

        role = request.args.get('role')
        if role:
            query = query.filter_by(role=role)

        neighbourhood = request.args.get('neighbourhood')
        if neighbourhood:
            query = query.filter_by(neighbourhood=neighbourhood)

        users = query.order_by(User.created_at.desc()).all()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Retrieve a single user by their ID."""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/api/users', methods=['POST'])
def create_user():
    """
    Create a new user account. Requires name and email.
    Role defaults to 'resident' if not specified.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        if 'name' not in data:
            return jsonify({'error': 'name is required'}), 400
        if 'email' not in data:
            return jsonify({'error': 'email is required'}), 400

        # Check for duplicate email
        existing = User.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({'error': 'Email already registered'}), 409

        user = User(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            address=data.get('address'),
            neighbourhood=data.get('neighbourhood'),
            role=data.get('role', 'resident')
        )

        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update an existing user account. Supports partial updates."""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            # Check uniqueness of new email
            if data['email'] != user.email:
                existing = User.query.filter_by(email=data['email']).first()
                if existing:
                    return jsonify({'error': 'Email already registered'}), 409
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        if 'address' in data:
            user.address = data['address']
        if 'neighbourhood' in data:
            user.neighbourhood = data['neighbourhood']
        if 'role' in data:
            user.role = data['role']

        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user account by their ID."""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/api/users/stats', methods=['GET'])
def get_user_stats():
    """Return aggregate statistics about users for the dashboard."""
    try:
        total = User.query.count()
        residents = User.query.filter_by(role='resident').count()
        authorities = User.query.filter_by(role='authority').count()
        admins = User.query.filter_by(role='admin').count()

        return jsonify({
            'total': total,
            'by_role': {
                'resident': residents,
                'authority': authorities,
                'admin': admins
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
