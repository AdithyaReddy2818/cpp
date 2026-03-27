"""
AlertEngine module for the SafeZone library.
Implements notification rules, radius-based alerts, escalation logic,
and alert fatigue prevention for community safety systems.
Author: Adithya Reddy Madireddy
"""

import math
from datetime import datetime, timedelta
from collections import defaultdict


class AlertEngine:
    """
    Manages alert generation and delivery for safety incidents.
    Supports radius-based alerting, escalation chains, cool-down periods
    to prevent notification fatigue, and per-user channel preferences.
    """

    def __init__(self, default_radius_km=2.0, cooldown_minutes=30):
        """
        Initialize the alert engine with configurable defaults.

        Args:
            default_radius_km: Default alert radius in kilometres.
            cooldown_minutes: Minimum minutes between alerts to the same user.
        """
        self._default_radius = default_radius_km
        self._cooldown_minutes = cooldown_minutes
        self._subscribers = {}  # user_id -> subscriber info
        self._alert_history = []  # list of all generated alerts
        self._user_last_alert = {}  # user_id -> last alert datetime
        self._escalation_chains = {}  # zone_id -> list of authority levels
        self._channel_preferences = {}  # user_id -> preferred channels

    def add_subscriber(self, user_id, name, latitude, longitude, email=None, phone=None):
        """
        Register a subscriber who can receive alerts about nearby incidents.

        Args:
            user_id: Unique identifier for the user.
            name: The subscriber's display name.
            latitude: Home or preferred latitude for proximity calculations.
            longitude: Home or preferred longitude.
            email: Optional email address for email alerts.
            phone: Optional phone number for SMS alerts.
        """
        self._subscribers[user_id] = {
            'name': name,
            'latitude': latitude,
            'longitude': longitude,
            'email': email,
            'phone': phone
        }

    def remove_subscriber(self, user_id):
        """Remove a subscriber from the alert system."""
        self._subscribers.pop(user_id, None)
        self._channel_preferences.pop(user_id, None)

    def set_channel_preference(self, user_id, channels):
        """
        Set preferred notification channels for a user.

        Args:
            user_id: The subscriber's unique identifier.
            channels: List of channel strings, e.g. ['email', 'sms', 'push'].
        """
        self._channel_preferences[user_id] = channels

    def get_channel_preference(self, user_id):
        """Get the notification channels preferred by a user. Defaults to email."""
        return self._channel_preferences.get(user_id, ['email'])

    def set_escalation_chain(self, zone_id, chain):
        """
        Define an escalation chain for a neighbourhood zone.
        The chain is an ordered list of authority levels to notify
        as an incident's severity increases.

        Args:
            zone_id: The zone identifier.
            chain: List of dicts with 'level', 'contact', and 'min_severity' keys.
        """
        self._escalation_chains[zone_id] = sorted(chain, key=lambda c: c['min_severity'])

    def get_escalation_contacts(self, zone_id, severity_score):
        """
        Get the appropriate escalation contacts for a given zone and severity.
        Returns all contacts whose minimum severity threshold is met.
        """
        chain = self._escalation_chains.get(zone_id, [])
        return [c for c in chain if severity_score >= c['min_severity']]

    def generate_alerts(self, incident_lat, incident_lng, incident_title,
                        severity_score, radius_km=None, timestamp=None):
        """
        Generate alerts for all subscribers within the alert radius.
        Respects cool-down periods to prevent alert fatigue.

        Args:
            incident_lat: Incident latitude.
            incident_lng: Incident longitude.
            incident_title: Title of the incident for the alert message.
            severity_score: Numeric severity (0-100).
            radius_km: Alert radius; uses default if not specified.
            timestamp: Alert generation time; defaults to now.
        Returns:
            List of alert dictionaries that were generated.
        """
        if radius_km is None:
            radius_km = self._default_radius
        if timestamp is None:
            timestamp = datetime.now()

        alerts = []
        for user_id, sub in self._subscribers.items():
            dist = self._haversine(
                incident_lat, incident_lng,
                sub['latitude'], sub['longitude']
            )
            if dist <= radius_km:
                if self._is_in_cooldown(user_id, timestamp):
                    continue
                alert = {
                    'user_id': user_id,
                    'user_name': sub['name'],
                    'channels': self.get_channel_preference(user_id),
                    'incident_title': incident_title,
                    'severity': severity_score,
                    'distance_km': round(dist, 3),
                    'timestamp': timestamp.isoformat()
                }
                alerts.append(alert)
                self._alert_history.append(alert)
                self._user_last_alert[user_id] = timestamp

        return alerts

    def _is_in_cooldown(self, user_id, current_time):
        """
        Check whether a user is currently in the alert cool-down period.
        Prevents notification fatigue by enforcing a minimum interval.
        """
        last = self._user_last_alert.get(user_id)
        if last is None:
            return False
        delta = current_time - last
        return delta < timedelta(minutes=self._cooldown_minutes)

    def set_cooldown(self, minutes):
        """Update the global cool-down period in minutes."""
        self._cooldown_minutes = minutes

    def get_alert_history(self, user_id=None):
        """
        Retrieve the alert history, optionally filtered by user.

        Args:
            user_id: If provided, return only alerts for this user.
        Returns:
            List of alert dictionaries.
        """
        if user_id:
            return [a for a in self._alert_history if a['user_id'] == user_id]
        return list(self._alert_history)

    def get_alert_count_by_user(self):
        """Return a dictionary mapping each user_id to their total alert count."""
        counts = defaultdict(int)
        for alert in self._alert_history:
            counts[alert['user_id']] += 1
        return dict(counts)

    def clear_history(self):
        """Clear all alert history and cooldown records."""
        self._alert_history.clear()
        self._user_last_alert.clear()

    def calculate_alert_radius(self, severity_score):
        """
        Dynamically calculate the alert radius based on severity.
        Higher severity incidents alert a wider area.

        Returns:
            Radius in kilometres.
        """
        if severity_score >= 80:
            return self._default_radius * 2.5
        elif severity_score >= 60:
            return self._default_radius * 1.5
        elif severity_score >= 40:
            return self._default_radius
        else:
            return self._default_radius * 0.5

    def _haversine(self, lat1, lng1, lat2, lng2):
        """Calculate great-circle distance in km using the Haversine formula."""
        r = 6371.0
        d_lat = math.radians(lat2 - lat1)
        d_lng = math.radians(lng2 - lng1)
        a = (math.sin(d_lat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(d_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c
