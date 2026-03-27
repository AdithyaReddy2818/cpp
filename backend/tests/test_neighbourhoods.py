"""
Tests for neighbourhood CRUD operations and related endpoints.
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


def _create_neighbourhood(client, name='Rathmines', zone_code='DCC-01'):
    """Helper to create a neighbourhood and return the response."""
    return client.post('/api/neighbourhoods', json={
        'name': name,
        'zone_code': zone_code,
        'description': 'A vibrant neighbourhood in Dublin',
        'contact_authority': 'Inspector Murphy',
        'contact_email': 'murphy@garda.ie',
        'contact_phone': '0851234567',
        'population': 15000,
        'boundaries': [[53.32, -6.27], [53.33, -6.27], [53.33, -6.26], [53.32, -6.26]]
    })


class TestNeighbourhoodCRUD:
    """Test suite for neighbourhood CRUD operations."""

    def test_create_neighbourhood_success(self, client):
        """Test creating a valid neighbourhood returns 201."""
        resp = _create_neighbourhood(client)
        assert resp.status_code == 201
        assert resp.get_json()['name'] == 'Rathmines'
        assert resp.get_json()['zone_code'] == 'DCC-01'

    def test_create_neighbourhood_missing_name(self, client):
        """Test creating a neighbourhood without name returns 400."""
        resp = client.post('/api/neighbourhoods', json={'zone_code': 'X-01'})
        assert resp.status_code == 400

    def test_create_neighbourhood_missing_zone_code(self, client):
        """Test creating a neighbourhood without zone_code returns 400."""
        resp = client.post('/api/neighbourhoods', json={'name': 'Test'})
        assert resp.status_code == 400

    def test_create_neighbourhood_duplicate_zone(self, client):
        """Test creating a neighbourhood with duplicate zone_code returns 409."""
        _create_neighbourhood(client)
        resp = _create_neighbourhood(client, name='Other', zone_code='DCC-01')
        assert resp.status_code == 409

    def test_get_all_neighbourhoods(self, client):
        """Test retrieving all neighbourhoods returns a list."""
        _create_neighbourhood(client, 'A', 'A-01')
        _create_neighbourhood(client, 'B', 'B-01')
        resp = client.get('/api/neighbourhoods')
        assert resp.status_code == 200
        assert len(resp.get_json()) == 2

    def test_get_single_neighbourhood(self, client):
        """Test retrieving a single neighbourhood by ID."""
        create_resp = _create_neighbourhood(client)
        nid = create_resp.get_json()['id']
        resp = client.get(f'/api/neighbourhoods/{nid}')
        assert resp.status_code == 200
        assert resp.get_json()['name'] == 'Rathmines'

    def test_get_nonexistent_neighbourhood(self, client):
        """Test retrieving a nonexistent neighbourhood returns 404."""
        resp = client.get('/api/neighbourhoods/9999')
        assert resp.status_code == 404

    def test_update_neighbourhood(self, client):
        """Test updating a neighbourhood modifies the correct fields."""
        create_resp = _create_neighbourhood(client)
        nid = create_resp.get_json()['id']
        resp = client.put(f'/api/neighbourhoods/{nid}', json={
            'name': 'Updated Rathmines', 'population': 20000
        })
        assert resp.status_code == 200
        assert resp.get_json()['name'] == 'Updated Rathmines'
        assert resp.get_json()['population'] == 20000

    def test_delete_neighbourhood(self, client):
        """Test deleting a neighbourhood removes it."""
        create_resp = _create_neighbourhood(client)
        nid = create_resp.get_json()['id']
        resp = client.delete(f'/api/neighbourhoods/{nid}')
        assert resp.status_code == 200
        get_resp = client.get(f'/api/neighbourhoods/{nid}')
        assert get_resp.status_code == 404

    def test_delete_nonexistent_neighbourhood(self, client):
        """Test deleting a nonexistent neighbourhood returns 404."""
        resp = client.delete('/api/neighbourhoods/9999')
        assert resp.status_code == 404

    def test_neighbourhood_stats(self, client):
        """Test the neighbourhood stats endpoint returns correct data."""
        _create_neighbourhood(client, 'A', 'A-01')
        _create_neighbourhood(client, 'B', 'B-01')
        resp = client.get('/api/neighbourhoods/stats')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['total_neighbourhoods'] == 2
        assert data['total_population'] == 30000

    def test_neighbourhood_boundaries_stored(self, client):
        """Test that boundary coordinates are stored and retrieved correctly."""
        create_resp = _create_neighbourhood(client)
        nid = create_resp.get_json()['id']
        resp = client.get(f'/api/neighbourhoods/{nid}')
        data = resp.get_json()
        assert data['boundaries'] is not None
        assert len(data['boundaries']) == 4
