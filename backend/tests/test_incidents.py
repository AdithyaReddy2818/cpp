"""
Tests for incident CRUD operations and related endpoints.
Covers creation, retrieval, update, deletion, status changes, photo uploads, and statistics.
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


def _create_user(client, name='Test User', email='test@example.com'):
    """Helper to create a user and return the response data."""
    return client.post('/api/users', json={
        'name': name, 'email': email, 'role': 'resident',
        'neighbourhood': 'Dublin City Centre'
    })


def _create_incident(client, reporter_id, title='Broken Window'):
    """Helper to create an incident and return the response data."""
    return client.post('/api/incidents', json={
        'title': title,
        'description': 'Window smashed on Main Street',
        'category': 'vandalism',
        'severity': 'medium',
        'reporter_id': reporter_id,
        'latitude': 53.3498,
        'longitude': -6.2603,
        'address': '10 Main Street, Dublin',
        'neighbourhood_zone': 'DCC-01'
    })


class TestIncidentCRUD:
    """Test suite for incident CRUD operations."""

    def test_create_incident_success(self, client):
        """Test creating a valid incident returns 201 with correct data."""
        user_resp = _create_user(client)
        user_id = user_resp.get_json()['id']
        resp = _create_incident(client, user_id)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['title'] == 'Broken Window'
        assert data['category'] == 'vandalism'
        assert data['status'] == 'reported'

    def test_create_incident_missing_fields(self, client):
        """Test creating an incident with missing required fields returns 400."""
        user_resp = _create_user(client)
        user_id = user_resp.get_json()['id']
        resp = client.post('/api/incidents', json={'title': 'Incomplete', 'reporter_id': user_id})
        assert resp.status_code == 400

    def test_create_incident_invalid_reporter(self, client):
        """Test creating an incident with a nonexistent reporter returns 404."""
        resp = client.post('/api/incidents', json={
            'title': 'Test', 'description': 'Desc',
            'category': 'theft', 'reporter_id': 9999
        })
        assert resp.status_code == 404

    def test_get_all_incidents(self, client):
        """Test retrieving all incidents returns a list."""
        user_resp = _create_user(client)
        user_id = user_resp.get_json()['id']
        _create_incident(client, user_id, 'Incident 1')
        _create_incident(client, user_id, 'Incident 2')
        resp = client.get('/api/incidents')
        assert resp.status_code == 200
        assert len(resp.get_json()) == 2

    def test_get_single_incident(self, client):
        """Test retrieving a single incident by ID returns the correct data."""
        user_resp = _create_user(client)
        user_id = user_resp.get_json()['id']
        create_resp = _create_incident(client, user_id)
        incident_id = create_resp.get_json()['id']
        resp = client.get(f'/api/incidents/{incident_id}')
        assert resp.status_code == 200
        assert resp.get_json()['title'] == 'Broken Window'

    def test_get_nonexistent_incident(self, client):
        """Test retrieving a nonexistent incident returns 404."""
        resp = client.get('/api/incidents/9999')
        assert resp.status_code == 404

    def test_update_incident(self, client):
        """Test updating an incident modifies the correct fields."""
        user_resp = _create_user(client)
        user_id = user_resp.get_json()['id']
        create_resp = _create_incident(client, user_id)
        incident_id = create_resp.get_json()['id']
        resp = client.put(f'/api/incidents/{incident_id}', json={
            'title': 'Updated Title', 'severity': 'high'
        })
        assert resp.status_code == 200
        assert resp.get_json()['title'] == 'Updated Title'
        assert resp.get_json()['severity'] == 'high'

    def test_delete_incident(self, client):
        """Test deleting an incident removes it from the database."""
        user_resp = _create_user(client)
        user_id = user_resp.get_json()['id']
        create_resp = _create_incident(client, user_id)
        incident_id = create_resp.get_json()['id']
        resp = client.delete(f'/api/incidents/{incident_id}')
        assert resp.status_code == 200
        get_resp = client.get(f'/api/incidents/{incident_id}')
        assert get_resp.status_code == 404

    def test_update_incident_status(self, client):
        """Test patching incident status transitions correctly."""
        user_resp = _create_user(client)
        user_id = user_resp.get_json()['id']
        create_resp = _create_incident(client, user_id)
        incident_id = create_resp.get_json()['id']
        resp = client.patch(f'/api/incidents/{incident_id}/status', json={
            'status': 'investigating'
        })
        assert resp.status_code == 200
        assert resp.get_json()['status'] == 'investigating'

    def test_update_incident_invalid_status(self, client):
        """Test patching with invalid status returns 400."""
        user_resp = _create_user(client)
        user_id = user_resp.get_json()['id']
        create_resp = _create_incident(client, user_id)
        incident_id = create_resp.get_json()['id']
        resp = client.patch(f'/api/incidents/{incident_id}/status', json={
            'status': 'invalid_status'
        })
        assert resp.status_code == 400

    def test_incident_photo_upload(self, client):
        """Test adding a photo URL to an incident."""
        user_resp = _create_user(client)
        user_id = user_resp.get_json()['id']
        create_resp = _create_incident(client, user_id)
        incident_id = create_resp.get_json()['id']
        resp = client.post(f'/api/incidents/{incident_id}/photos', json={
            'photo_url': 'https://example.com/photo1.jpg'
        })
        assert resp.status_code == 200
        assert 'https://example.com/photo1.jpg' in resp.get_json()['photo_urls']

    def test_incident_stats(self, client):
        """Test the statistics endpoint returns correct aggregate data."""
        user_resp = _create_user(client)
        user_id = user_resp.get_json()['id']
        _create_incident(client, user_id, 'Incident 1')
        _create_incident(client, user_id, 'Incident 2')
        resp = client.get('/api/incidents/stats')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['total'] == 2

    def test_filter_incidents_by_category(self, client):
        """Test filtering incidents by category query parameter."""
        user_resp = _create_user(client)
        user_id = user_resp.get_json()['id']
        _create_incident(client, user_id, 'Vandalism Case')
        client.post('/api/incidents', json={
            'title': 'Theft Case', 'description': 'Stolen bicycle',
            'category': 'theft', 'reporter_id': user_id
        })
        resp = client.get('/api/incidents?category=theft')
        assert resp.status_code == 200
        assert len(resp.get_json()) == 1
        assert resp.get_json()[0]['category'] == 'theft'
