"""
Comment routes for full CRUD operations on incident comments.
Allows residents and authorities to discuss and track incident updates.
Author: Adithya Reddy Madireddy
"""

from flask import Blueprint, request, jsonify
from models.database import db
from models.comment import Comment
from models.incident import Incident
from models.user import User

comment_bp = Blueprint('comments', __name__)


@comment_bp.route('/api/comments', methods=['GET'])
def get_comments():
    """Retrieve all comments, with optional filtering by incident or user."""
    try:
        query = Comment.query

        incident_id = request.args.get('incident_id')
        if incident_id:
            query = query.filter_by(incident_id=int(incident_id))

        user_id = request.args.get('user_id')
        if user_id:
            query = query.filter_by(user_id=int(user_id))

        comments = query.order_by(Comment.created_at.desc()).all()
        return jsonify([comment.to_dict() for comment in comments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@comment_bp.route('/api/comments/<int:comment_id>', methods=['GET'])
def get_comment(comment_id):
    """Retrieve a single comment by its ID."""
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
        return jsonify(comment.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@comment_bp.route('/api/comments', methods=['POST'])
def create_comment():
    """
    Create a new comment on an incident. Requires text, incident_id, and user_id.
    Validates that both the incident and user exist before creating.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        required = ['text', 'incident_id', 'user_id']
        for field in required:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Verify incident exists
        incident = Incident.query.get(data['incident_id'])
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404

        # Verify user exists
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404

        comment = Comment(
            text=data['text'],
            incident_id=data['incident_id'],
            user_id=data['user_id']
        )

        db.session.add(comment)
        db.session.commit()
        return jsonify(comment.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@comment_bp.route('/api/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    """Update the text of an existing comment."""
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        if 'text' in data:
            comment.text = data['text']

        db.session.commit()
        return jsonify(comment.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@comment_bp.route('/api/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """Delete a comment by its ID."""
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404

        db.session.delete(comment)
        db.session.commit()
        return jsonify({'message': 'Comment deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@comment_bp.route('/api/incidents/<int:incident_id>/comments', methods=['GET'])
def get_incident_comments(incident_id):
    """Retrieve all comments for a specific incident."""
    try:
        incident = Incident.query.get(incident_id)
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404

        comments = Comment.query.filter_by(incident_id=incident_id)\
            .order_by(Comment.created_at.asc()).all()
        return jsonify([comment.to_dict() for comment in comments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
