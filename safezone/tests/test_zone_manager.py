"""
Tests for the ZoneManager class.
Author: Adithya Reddy Madireddy
"""

import pytest
from safezone.zone_manager import ZoneManager


@pytest.fixture
def zm():
    """Provide a ZoneManager with a predefined rectangular zone."""
    manager = ZoneManager()
    # A rectangular zone around Dublin city centre
    polygon = [
        (53.34, -6.28),
        (53.36, -6.28),
        (53.36, -6.24),
        (53.34, -6.24)
    ]
    manager.add_zone('DCC-01', 'Dublin City Centre', polygon)
    return manager


class TestZoneManager:

    def test_add_zone(self, zm):
        """Adding a zone should register it in the manager."""
        zones = zm.list_zones()
        assert len(zones) == 1
        assert zones[0]['zone_id'] == 'DCC-01'

    def test_add_zone_invalid_polygon(self, zm):
        """Adding a zone with fewer than 3 vertices should raise ValueError."""
        with pytest.raises(ValueError):
            zm.add_zone('X', 'Bad Zone', [(1, 2)])

    def test_remove_zone(self, zm):
        """Removing a zone should delete it from the registry."""
        zm.remove_zone('DCC-01')
        assert len(zm.list_zones()) == 0

    def test_remove_nonexistent_zone(self, zm):
        """Removing a nonexistent zone should raise KeyError."""
        with pytest.raises(KeyError):
            zm.remove_zone('FAKE')

    def test_get_zone(self, zm):
        """Getting a zone by ID should return its data."""
        zone = zm.get_zone('DCC-01')
        assert zone['name'] == 'Dublin City Centre'

    def test_point_in_zone_inside(self, zm):
        """A point inside the polygon should return True."""
        assert zm.point_in_zone(53.35, -6.26, 'DCC-01') is True

    def test_point_in_zone_outside(self, zm):
        """A point outside the polygon should return False."""
        assert zm.point_in_zone(53.30, -6.20, 'DCC-01') is False

    def test_find_zone_for_point(self, zm):
        """Should identify the correct zone for a point inside it."""
        assert zm.find_zone_for_point(53.35, -6.26) == 'DCC-01'

    def test_find_zone_for_point_none(self, zm):
        """Should return None when the point is not in any zone."""
        assert zm.find_zone_for_point(54.0, -7.0) is None

    def test_calculate_distance(self, zm):
        """Distance between two known points should be approximately correct."""
        dist = zm.calculate_distance(53.34, -6.26, 53.35, -6.26)
        assert 1.0 < dist < 1.2  # About 1.11 km

    def test_find_nearby_zones(self, zm):
        """Should find zones within the given radius."""
        nearby = zm.find_nearby_zones(53.35, -6.26, 5.0)
        assert len(nearby) == 1
        assert nearby[0]['zone_id'] == 'DCC-01'

    def test_find_nearby_zones_empty(self, zm):
        """Should return empty list when no zones are near."""
        nearby = zm.find_nearby_zones(54.5, -7.5, 1.0)
        assert len(nearby) == 0

    def test_register_incident(self, zm):
        """Registering incidents should increase the internal count."""
        zm.register_incident(53.35, -6.26, 'theft')
        zm.register_incident(53.35, -6.26, 'vandalism')
        assert len(zm._incidents) == 2

    def test_detect_hotspots(self, zm):
        """A cluster of nearby incidents should be detected as a hotspot."""
        for i in range(5):
            zm.register_incident(53.35 + i * 0.0001, -6.26, 'theft')
        hotspots = zm.detect_hotspots(radius_km=0.5, min_incidents=3)
        assert len(hotspots) >= 1
        assert hotspots[0]['incident_count'] >= 3

    def test_get_zone_incident_count(self, zm):
        """Should correctly count incidents per zone."""
        zm.register_incident(53.35, -6.26, 'theft')
        zm.register_incident(53.35, -6.26, 'vandalism')
        counts = zm.get_zone_incident_count()
        assert counts.get('DCC-01', 0) == 2
