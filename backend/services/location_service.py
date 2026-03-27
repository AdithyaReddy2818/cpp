"""
Amazon Location Service wrapper with mock and real implementations.
Provides geocoding, reverse geocoding, and map rendering support.
Author: Adithya Reddy Madireddy
"""

import uuid
from datetime import datetime, timezone


class LocationService:
    """
    Service class for interacting with Amazon Location Service.
    Provides geocoding of incident addresses and map-related features.
    In mock mode, returns realistic Dublin-area coordinates.
    """

    def __init__(self, app=None):
        """Initialize the Location service with optional Flask app configuration."""
        self.use_aws = False
        self.region = 'eu-west-1'
        self.index_name = 'safety-app-place-index'
        self.client = None
        # Mock geocoding database for common Dublin locations
        self._mock_locations = {
            'dublin': {'latitude': 53.3498, 'longitude': -6.2603},
            'grafton street': {'latitude': 53.3414, 'longitude': -6.2592},
            'o\'connell street': {'latitude': 53.3498, 'longitude': -6.2603},
            'temple bar': {'latitude': 53.3454, 'longitude': -6.2643},
            'smithfield': {'latitude': 53.3479, 'longitude': -6.2783},
            'phibsborough': {'latitude': 53.3590, 'longitude': -6.2722},
            'rathmines': {'latitude': 53.3223, 'longitude': -6.2654},
            'drumcondra': {'latitude': 53.3702, 'longitude': -6.2520},
            'ballsbridge': {'latitude': 53.3282, 'longitude': -6.2284},
            'clontarf': {'latitude': 53.3654, 'longitude': -6.1897},
        }
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Configure the service from the Flask app settings."""
        self.use_aws = app.config.get('USE_AWS', False)
        self.region = app.config.get('AWS_REGION', 'eu-west-1')
        self.index_name = app.config.get('LOCATION_INDEX_NAME', 'safety-app-place-index')
        if self.use_aws:
            import boto3
            self.client = boto3.client('location', region_name=self.region)

    def geocode_address(self, address):
        """
        Convert an address string to latitude and longitude coordinates.
        In mock mode, uses a local database of Dublin locations or generates
        realistic random coordinates within the Dublin area.

        Args:
            address: The address string to geocode.
        Returns:
            Dictionary with latitude, longitude, and formatted label.
        """
        if self.use_aws and self.client:
            response = self.client.search_place_index_for_text(
                IndexName=self.index_name,
                Text=address,
                MaxResults=1
            )
            if response['Results']:
                point = response['Results'][0]['Place']['Geometry']['Point']
                label = response['Results'][0]['Place'].get('Label', address)
                return {
                    'latitude': point[1],
                    'longitude': point[0],
                    'label': label,
                    'status': 'success'
                }
            return {'status': 'not_found', 'message': 'Address not found'}

        # Mock mode: look up in local database or return Dublin centre
        address_lower = address.lower().strip()
        for key, coords in self._mock_locations.items():
            if key in address_lower:
                return {
                    'latitude': coords['latitude'],
                    'longitude': coords['longitude'],
                    'label': f'{address}, Dublin, Ireland',
                    'status': 'success',
                    'source': 'mock'
                }
        # Default to Dublin city centre with slight offset
        import hashlib
        hash_val = int(hashlib.md5(address.encode()).hexdigest()[:8], 16)
        lat_offset = (hash_val % 1000) / 100000.0
        lng_offset = (hash_val % 500) / 100000.0
        return {
            'latitude': 53.3498 + lat_offset,
            'longitude': -6.2603 + lng_offset,
            'label': f'{address}, Dublin, Ireland',
            'status': 'success',
            'source': 'mock'
        }

    def reverse_geocode(self, latitude, longitude):
        """
        Convert coordinates to a human-readable address.

        Args:
            latitude: The latitude coordinate.
            longitude: The longitude coordinate.
        Returns:
            Dictionary with address label and details.
        """
        if self.use_aws and self.client:
            response = self.client.search_place_index_for_position(
                IndexName=self.index_name,
                Position=[longitude, latitude],
                MaxResults=1
            )
            if response['Results']:
                place = response['Results'][0]['Place']
                return {
                    'label': place.get('Label', ''),
                    'neighbourhood': place.get('Neighborhood', ''),
                    'municipality': place.get('Municipality', ''),
                    'status': 'success'
                }
            return {'status': 'not_found'}

        # Mock mode: return a simulated Dublin address
        return {
            'label': f'{int(abs(latitude * 100) % 200)} Main Street, Dublin, Ireland',
            'neighbourhood': 'Dublin City Centre',
            'municipality': 'Dublin',
            'status': 'success',
            'source': 'mock'
        }

    def calculate_distance(self, lat1, lng1, lat2, lng2):
        """
        Calculate the distance in kilometres between two coordinate points
        using the Haversine formula.
        """
        import math
        r = 6371  # Earth radius in kilometres
        d_lat = math.radians(lat2 - lat1)
        d_lng = math.radians(lng2 - lng1)
        a = (math.sin(d_lat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(d_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(r * c, 3)

    def get_status(self):
        """Return the current status of the Location service for health checks."""
        if self.use_aws:
            try:
                self.client.describe_place_index(IndexName=self.index_name)
                return {
                    'service': 'Amazon Location Service',
                    'status': 'connected',
                    'mode': 'production',
                    'index': self.index_name,
                    'region': self.region
                }
            except Exception as e:
                return {
                    'service': 'Amazon Location Service',
                    'status': 'error',
                    'mode': 'production',
                    'error': str(e)
                }
        return {
            'service': 'Amazon Location Service',
            'status': 'mock',
            'mode': 'development',
            'mock_locations_count': len(self._mock_locations)
        }
