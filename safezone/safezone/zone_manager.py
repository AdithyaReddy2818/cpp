"""
ZoneManager module for the SafeZone library.
Handles neighbourhood boundary management, point-in-zone detection,
proximity calculations, and hotspot identification.
Author: Adithya Reddy Madireddy
"""

import math
from collections import defaultdict


class ZoneManager:
    """
    Manages neighbourhood zones defined as polygons on a coordinate plane.
    Provides spatial queries for determining which zone a point falls in,
    calculating distances between points, and detecting incident hotspots.
    """

    def __init__(self):
        """Initialize the zone manager with an empty zone registry."""
        self._zones = {}
        self._incidents = []

    def add_zone(self, zone_id, name, polygon):
        """
        Register a neighbourhood zone with its boundary polygon.

        Args:
            zone_id: Unique identifier for the zone.
            name: Human-readable zone name.
            polygon: List of (latitude, longitude) tuples defining the boundary.
                     The polygon should be closed (first point equals last).
        """
        if not polygon or len(polygon) < 3:
            raise ValueError("A polygon must have at least 3 vertices.")
        self._zones[zone_id] = {
            'name': name,
            'polygon': polygon,
            'centroid': self._calculate_centroid(polygon)
        }

    def remove_zone(self, zone_id):
        """Remove a zone from the registry by its ID."""
        if zone_id not in self._zones:
            raise KeyError(f"Zone '{zone_id}' not found.")
        del self._zones[zone_id]

    def get_zone(self, zone_id):
        """Retrieve zone information by its ID."""
        if zone_id not in self._zones:
            raise KeyError(f"Zone '{zone_id}' not found.")
        return self._zones[zone_id]

    def list_zones(self):
        """Return a list of all registered zones with their metadata."""
        return [
            {'zone_id': zid, 'name': z['name'], 'centroid': z['centroid']}
            for zid, z in self._zones.items()
        ]

    def point_in_zone(self, latitude, longitude, zone_id):
        """
        Determine whether a coordinate point lies inside a specific zone.
        Uses the ray-casting algorithm for point-in-polygon detection.

        Args:
            latitude: The point's latitude.
            longitude: The point's longitude.
            zone_id: The zone to test against.
        Returns:
            True if the point is inside the zone polygon.
        """
        zone = self._zones.get(zone_id)
        if not zone:
            raise KeyError(f"Zone '{zone_id}' not found.")
        return self._ray_casting(latitude, longitude, zone['polygon'])

    def find_zone_for_point(self, latitude, longitude):
        """
        Find which zone a coordinate point belongs to by testing
        it against all registered zone polygons.

        Returns:
            The zone_id of the matching zone, or None if no zone matches.
        """
        for zone_id, zone in self._zones.items():
            if self._ray_casting(latitude, longitude, zone['polygon']):
                return zone_id
        return None

    def calculate_distance(self, lat1, lng1, lat2, lng2):
        """
        Calculate the great-circle distance between two coordinate points
        using the Haversine formula.

        Returns:
            Distance in kilometres.
        """
        r = 6371.0  # Earth radius in km
        d_lat = math.radians(lat2 - lat1)
        d_lng = math.radians(lng2 - lng1)
        a = (math.sin(d_lat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(d_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(r * c, 4)

    def find_nearby_zones(self, latitude, longitude, radius_km):
        """
        Find all zones whose centroids are within a given radius of a point.

        Args:
            latitude: Centre point latitude.
            longitude: Centre point longitude.
            radius_km: Search radius in kilometres.
        Returns:
            List of zone dictionaries within the radius.
        """
        nearby = []
        for zone_id, zone in self._zones.items():
            clat, clng = zone['centroid']
            dist = self.calculate_distance(latitude, longitude, clat, clng)
            if dist <= radius_km:
                nearby.append({
                    'zone_id': zone_id,
                    'name': zone['name'],
                    'distance_km': dist
                })
        return sorted(nearby, key=lambda x: x['distance_km'])

    def register_incident(self, latitude, longitude, category='other', severity=50):
        """
        Register an incident location for hotspot analysis.
        Incidents are stored as coordinate-category pairs for density calculations.
        """
        self._incidents.append({
            'latitude': latitude,
            'longitude': longitude,
            'category': category,
            'severity': severity
        })

    def detect_hotspots(self, radius_km=0.5, min_incidents=3):
        """
        Identify hotspot areas where incident density exceeds a threshold.
        Uses a simple density-based clustering approach: for each incident,
        count how many other incidents fall within the given radius.

        Args:
            radius_km: The radius within which to count incidents.
            min_incidents: Minimum number of nearby incidents to qualify as hotspot.
        Returns:
            List of hotspot dictionaries with centre coordinates and density.
        """
        hotspots = []
        visited = set()

        for i, inc in enumerate(self._incidents):
            if i in visited:
                continue
            cluster = [i]
            for j, other in enumerate(self._incidents):
                if i == j:
                    continue
                dist = self.calculate_distance(
                    inc['latitude'], inc['longitude'],
                    other['latitude'], other['longitude']
                )
                if dist <= radius_km:
                    cluster.append(j)

            if len(cluster) >= min_incidents:
                for idx in cluster:
                    visited.add(idx)
                # Calculate cluster centroid
                lats = [self._incidents[idx]['latitude'] for idx in cluster]
                lngs = [self._incidents[idx]['longitude'] for idx in cluster]
                hotspots.append({
                    'centre_lat': sum(lats) / len(lats),
                    'centre_lng': sum(lngs) / len(lngs),
                    'incident_count': len(cluster),
                    'radius_km': radius_km
                })

        return hotspots

    def get_zone_incident_count(self):
        """
        Count the number of registered incidents per zone.
        Returns a dictionary mapping zone_id to incident count.
        """
        counts = defaultdict(int)
        for inc in self._incidents:
            zone_id = self.find_zone_for_point(inc['latitude'], inc['longitude'])
            if zone_id:
                counts[zone_id] += 1
        return dict(counts)

    def _ray_casting(self, lat, lng, polygon):
        """
        Ray-casting algorithm to determine if a point is inside a polygon.
        Counts the number of times a ray from the point crosses polygon edges.
        An odd number of crossings means the point is inside.
        Polygon vertices are stored as (latitude, longitude) tuples.
        """
        n = len(polygon)
        inside = False
        j = n - 1
        for i in range(n):
            lat_i, lng_i = polygon[i]
            lat_j, lng_j = polygon[j]
            if ((lng_i > lng) != (lng_j > lng)) and \
               (lat < (lat_j - lat_i) * (lng - lng_i) / (lng_j - lng_i) + lat_i):
                inside = not inside
            j = i
        return inside

    def _calculate_centroid(self, polygon):
        """Calculate the centroid (geometric centre) of a polygon."""
        n = len(polygon)
        lat_sum = sum(p[0] for p in polygon)
        lng_sum = sum(p[1] for p in polygon)
        return (lat_sum / n, lng_sum / n)
