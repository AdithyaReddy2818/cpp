"""
Tests for comment CRUD operations and related endpoints.
Author: Adithya Reddy Madireddy
"""

import json
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import create_app
from models.database import db


@pytest.fixture
def client():
    """Create a test client with a fresh in-memory database for each test."""
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


def _setup_user_and_incident(client):
    """Helper to create a user and an incident, returning both IDs."""
    user_resp = client.post('/api/users', json={
        'name': 'Commenter', 'email': 'commenter@example.com'
    })
    user_id = user_resp.get_json()['id']
    incident_resp = client.post('/api/incidents', json={
        'title': 'Test Incident', 'description': 'A test incident',
        'category': 'vandalism', 'reporter_id': user_id
    })
    incident_id = incident_resp.get_json()['id']
    return user_id, incident_id


class TestCommentCRUD:
    """Test suite for comment CRUD operations."""

    def test_create_comment_success(self, client):
        """Test creating a valid comment returns 201."""
        user_id, incident_id = _setup_user_and_incident(client)
        resp = client.post('/api/comments', json={
            'text': 'This is very concerning.',
            'incident_id': incident_id,
            'user_id': user_id
        })
        assert resp.status_code == 201
        assert resp.get_json()['text'] == 'This is very concerning.'

    def test_create_comment_missing_text(self, client):
        """Test creating a comment without text returns 400."""
        user_id, incident_id = _setup_user_and_incident(client)
        resp = client.post('/api/comments', json={
            'incident_id': incident_id, 'user_id': user_id
        })
        assert resp.status_code == 400

    def test_create_comment_invalid_incident(self, client):
        """Test creating a comment on nonexistent incident returns 404."""
        user_resp = client.post('/api/users', json={
            'name': 'User', 'email': 'u@example.com'
        })
        user_id = user_resp.get_json()['id']
        resp = client.post('/api/comments', json={
            'text': 'Comment', 'incident_id': 9999, 'user_id': user_id
        })
        assert resp.status_code == 404

    def test_create_comment_invalid_user(self, client):
        """Test creating a comment by nonexistent user returns 404."""
        user_resp = client.post('/api/users', json={
            'name': 'User', 'email': 'u2@example.com'
        })
        user_id = user_resp.get_json()['id']
        incident_resp = client.post('/api/incidents', json={
            'title': 'Inc', 'description': 'D', 'category': 'theft', 'reporter_id': user_id
        })
        incident_id = incident_resp.get_json()['id']
        resp = client.post('/api/comments', json={
            'text': 'Comment', 'incident_id': incident_id, 'user_id': 9999
        })
        assert resp.status_code == 404

    def test_get_all_comments(self, client):
        """Test retrieving all comments returns a list."""
        user_id, incident_id = _setup_user_and_incident(client)
        client.post('/api/comments', json={
            'text': 'Comment 1', 'incident_id': incident_id, 'user_id': user_id
        })
        client.post('/api/comments', json={
            'text': 'Comment 2', 'incident_id': incident_id, 'user_id': user_id
        })
        resp = client.get('/api/comments')
        assert resp.status_code == 200
        assert len(resp.get_json()) == 2

    def test_get_single_comment(self, client):
        """Test retrieving a single comment by ID."""
        user_id, incident_id = _setup_user_and_incident(client)
        create_resp = client.post('/api/comments', json={
            'text': 'My Comment', 'incident_id': incident_id, 'user_id': user_id
        })
        comment_id = create_resp.get_json()['id']
        resp = client.get(f'/api/comments/{comment_id}')
        assert resp.status_code == 200
        assert resp.get_json()['text'] == 'My Comment'

    def test_get_nonexistent_comment(self, client):
        """Test retrieving a nonexistent comment returns 404."""
        resp = client.get('/api/comments/9999')
        assert resp.status_code == 404

    def test_update_comment(self, client):
        """Test updating a comment text succeeds."""
        user_id, incident_id = _setup_user_and_incident(client)
        create_resp = client.post('/api/comments', json={
            'text': 'Old text', 'incident_id': incident_id, 'user_id': user_id
        })
        comment_id = create_resp.get_json()['id']
        resp = client.put(f'/api/comments/{comment_id}', json={
            'text': 'Updated text'
        })
        assert resp.status_code == 200
        assert resp.get_json()['text'] == 'Updated text'

    def test_delete_comment(self, client):
        """Test deleting a comment removes it."""
        user_id, incident_id = _setup_user_and_incident(client)
        create_resp = client.post('/api/comments', json={
            'text': 'To delete', 'incident_id': incident_id, 'user_id': user_id
        })
        comment_id = create_resp.get_json()['id']
        resp = client.delete(f'/api/comments/{comment_id}')
        assert resp.status_code == 200
        get_resp = client.get(f'/api/comments/{comment_id}')
        assert get_resp.status_code == 404

    def test_get_incident_comments(self, client):
        """Test retrieving comments for a specific incident."""
        user_id, incident_id = _setup_user_and_incident(client)
        client.post('/api/comments', json={
            'text': 'Comment A', 'incident_id': incident_id, 'user_id': user_id
        })
        resp = client.get(f'/api/incidents/{incident_id}/comments')
        assert resp.status_code == 200
        assert len(resp.get_json()) == 1

    def test_filter_comments_by_incident(self, client):
        """Test filtering comments by incident_id query parameter."""
        user_id, incident_id = _setup_user_and_incident(client)
        client.post('/api/comments', json={
            'text': 'Filtered', 'incident_id': incident_id, 'user_id': user_id
        })
        resp = client.get(f'/api/comments?incident_id={incident_id}')
        assert resp.status_code == 200
        assert len(resp.get_json()) >= 1
