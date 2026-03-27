"""
Tests for user CRUD operations and related endpoints.
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


class TestUserCRUD:
    """Test suite for user CRUD operations."""

    def test_create_user_success(self, client):
        """Test creating a valid user returns 201."""
        resp = client.post('/api/users', json={
            'name': 'John Doe', 'email': 'john@example.com',
            'role': 'resident', 'neighbourhood': 'Rathmines'
        })
        assert resp.status_code == 201
        assert resp.get_json()['name'] == 'John Doe'
        assert resp.get_json()['role'] == 'resident'

    def test_create_user_missing_name(self, client):
        """Test creating a user without name returns 400."""
        resp = client.post('/api/users', json={'email': 'noname@example.com'})
        assert resp.status_code == 400

    def test_create_user_missing_email(self, client):
        """Test creating a user without email returns 400."""
        resp = client.post('/api/users', json={'name': 'No Email'})
        assert resp.status_code == 400

    def test_create_user_duplicate_email(self, client):
        """Test creating a user with an existing email returns 409."""
        client.post('/api/users', json={
            'name': 'First', 'email': 'dup@example.com'
        })
        resp = client.post('/api/users', json={
            'name': 'Second', 'email': 'dup@example.com'
        })
        assert resp.status_code == 409

    def test_get_all_users(self, client):
        """Test retrieving all users returns a list."""
        client.post('/api/users', json={'name': 'A', 'email': 'a@example.com'})
        client.post('/api/users', json={'name': 'B', 'email': 'b@example.com'})
        resp = client.get('/api/users')
        assert resp.status_code == 200
        assert len(resp.get_json()) == 2

    def test_get_single_user(self, client):
        """Test retrieving a single user by ID."""
        create_resp = client.post('/api/users', json={
            'name': 'Jane', 'email': 'jane@example.com'
        })
        user_id = create_resp.get_json()['id']
        resp = client.get(f'/api/users/{user_id}')
        assert resp.status_code == 200
        assert resp.get_json()['name'] == 'Jane'

    def test_get_nonexistent_user(self, client):
        """Test retrieving a nonexistent user returns 404."""
        resp = client.get('/api/users/9999')
        assert resp.status_code == 404

    def test_update_user(self, client):
        """Test updating user fields succeeds."""
        create_resp = client.post('/api/users', json={
            'name': 'Old Name', 'email': 'old@example.com'
        })
        user_id = create_resp.get_json()['id']
        resp = client.put(f'/api/users/{user_id}', json={
            'name': 'New Name', 'phone': '0851234567'
        })
        assert resp.status_code == 200
        assert resp.get_json()['name'] == 'New Name'
        assert resp.get_json()['phone'] == '0851234567'

    def test_delete_user(self, client):
        """Test deleting a user removes it from the database."""
        create_resp = client.post('/api/users', json={
            'name': 'Delete Me', 'email': 'del@example.com'
        })
        user_id = create_resp.get_json()['id']
        resp = client.delete(f'/api/users/{user_id}')
        assert resp.status_code == 200
        get_resp = client.get(f'/api/users/{user_id}')
        assert get_resp.status_code == 404

    def test_delete_nonexistent_user(self, client):
        """Test deleting a nonexistent user returns 404."""
        resp = client.delete('/api/users/9999')
        assert resp.status_code == 404

    def test_filter_users_by_role(self, client):
        """Test filtering users by role query parameter."""
        client.post('/api/users', json={
            'name': 'Resident', 'email': 'r@example.com', 'role': 'resident'
        })
        client.post('/api/users', json={
            'name': 'Authority', 'email': 'a@example.com', 'role': 'authority'
        })
        resp = client.get('/api/users?role=authority')
        assert resp.status_code == 200
        assert len(resp.get_json()) == 1
        assert resp.get_json()[0]['role'] == 'authority'

    def test_user_stats(self, client):
        """Test the user stats endpoint returns correct data."""
        client.post('/api/users', json={
            'name': 'R1', 'email': 'r1@example.com', 'role': 'resident'
        })
        client.post('/api/users', json={
            'name': 'A1', 'email': 'a1@example.com', 'role': 'authority'
        })
        resp = client.get('/api/users/stats')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['total'] == 2
        assert data['by_role']['resident'] == 1
