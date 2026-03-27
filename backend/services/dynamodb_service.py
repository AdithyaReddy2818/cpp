"""
Amazon DynamoDB service wrapper with mock and real implementations.
Provides incident, user, and report storage in DynamoDB tables.
Author: Adithya Reddy Madireddy
"""

import uuid
import json
from datetime import datetime, timezone


class DynamoDBService:
    """
    Service class for interacting with Amazon DynamoDB.
    When USE_AWS is False, operations are simulated with an in-memory store
    to enable local development without AWS credentials.
    """

    def __init__(self, app=None):
        """Initialize the DynamoDB service with optional Flask app configuration."""
        self.use_aws = False
        self.region = 'eu-west-1'
        self.table_prefix = 'safety-app-'
        self.client = None
        # In-memory store for mock mode, keyed by table name
        self._mock_store = {}
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Configure the service from the Flask app settings."""
        self.use_aws = app.config.get('USE_AWS', False)
        self.region = app.config.get('AWS_REGION', 'eu-west-1')
        self.table_prefix = app.config.get('DYNAMODB_TABLE_PREFIX', 'safety-app-')
        if self.use_aws:
            import boto3
            self.client = boto3.resource('dynamodb', region_name=self.region)

    def _get_table_name(self, entity):
        """Build the full DynamoDB table name for a given entity type."""
        return f'{self.table_prefix}{entity}'

    def put_item(self, table_name, item):
        """
        Store an item in the specified DynamoDB table.
        In mock mode, items are stored in a dictionary keyed by table name.
        """
        full_table = self._get_table_name(table_name)
        if self.use_aws and self.client:
            table = self.client.Table(full_table)
            table.put_item(Item=item)
            return {'status': 'success', 'table': full_table}

        # Mock mode: store in memory
        if full_table not in self._mock_store:
            self._mock_store[full_table] = []
        self._mock_store[full_table].append(item)
        return {
            'status': 'success',
            'message': f'Mock: item stored in {full_table}',
            'item_id': item.get('id', str(uuid.uuid4()))
        }

    def get_item(self, table_name, key):
        """
        Retrieve a single item from a DynamoDB table by its key.
        Returns None if the item is not found.
        """
        full_table = self._get_table_name(table_name)
        if self.use_aws and self.client:
            table = self.client.Table(full_table)
            response = table.get_item(Key=key)
            return response.get('Item')

        # Mock mode: search the in-memory store
        items = self._mock_store.get(full_table, [])
        for item in items:
            match = all(item.get(k) == v for k, v in key.items())
            if match:
                return item
        return None

    def scan_table(self, table_name):
        """
        Scan all items from a DynamoDB table.
        Returns a list of all items stored in the table.
        """
        full_table = self._get_table_name(table_name)
        if self.use_aws and self.client:
            table = self.client.Table(full_table)
            response = table.scan()
            return response.get('Items', [])

        # Mock mode: return all items from the in-memory store
        return self._mock_store.get(full_table, [])

    def delete_item(self, table_name, key):
        """
        Delete an item from a DynamoDB table by its key.
        Returns a status dictionary indicating success or failure.
        """
        full_table = self._get_table_name(table_name)
        if self.use_aws and self.client:
            table = self.client.Table(full_table)
            table.delete_item(Key=key)
            return {'status': 'success', 'table': full_table}

        # Mock mode: remove from in-memory store
        items = self._mock_store.get(full_table, [])
        self._mock_store[full_table] = [
            item for item in items
            if not all(item.get(k) == v for k, v in key.items())
        ]
        return {'status': 'success', 'message': f'Mock: item deleted from {full_table}'}

    def get_status(self):
        """Return the current status of the DynamoDB service for health checks."""
        if self.use_aws:
            try:
                tables = list(self.client.tables.all())
                return {
                    'service': 'Amazon DynamoDB',
                    'status': 'connected',
                    'mode': 'production',
                    'region': self.region,
                    'tables_found': len(tables)
                }
            except Exception as e:
                return {
                    'service': 'Amazon DynamoDB',
                    'status': 'error',
                    'mode': 'production',
                    'error': str(e)
                }
        return {
            'service': 'Amazon DynamoDB',
            'status': 'mock',
            'mode': 'development',
            'tables': list(self._mock_store.keys()),
            'total_items': sum(len(v) for v in self._mock_store.values())
        }
