"""
Tests for the AlertEngine class.
Author: Adithya Reddy Madireddy
"""

import pytest
from datetime import datetime, timedelta
from safezone.alert_engine import AlertEngine


@pytest.fixture
def engine():
    """Provide an AlertEngine with two subscribers near Dublin city centre."""
    ae = AlertEngine(default_radius_km=2.0, cooldown_minutes=30)
    ae.add_subscriber('u1', 'Alice', 53.35, -6.26, email='alice@example.com')
    ae.add_subscriber('u2', 'Bob', 53.34, -6.27, phone='0851234567')
    return ae


class TestAlertEngine:

    def test_add_subscriber(self, engine):
        """Adding a subscriber should register them in the system."""
        assert 'u1' in engine._subscribers
        assert engine._subscribers['u1']['name'] == 'Alice'

    def test_remove_subscriber(self, engine):
        """Removing a subscriber should delete them."""
        engine.remove_subscriber('u1')
        assert 'u1' not in engine._subscribers

    def test_set_channel_preference(self, engine):
        """Setting channel preferences should store them for the user."""
        engine.set_channel_preference('u1', ['email', 'sms'])
        assert engine.get_channel_preference('u1') == ['email', 'sms']

    def test_default_channel_preference(self, engine):
        """Default channel preference should be email."""
        assert engine.get_channel_preference('u1') == ['email']

    def test_generate_alerts_within_radius(self, engine):
        """Subscribers within radius should receive alerts."""
        alerts = engine.generate_alerts(53.35, -6.26, 'Test Incident', 70)
        assert len(alerts) >= 1
        assert any(a['user_id'] == 'u1' for a in alerts)

    def test_generate_alerts_outside_radius(self, engine):
        """Subscribers outside radius should not receive alerts."""
        alerts = engine.generate_alerts(54.0, -7.0, 'Far Incident', 50)
        assert len(alerts) == 0

    def test_cooldown_prevents_duplicate(self, engine):
        """A second alert within cooldown should be suppressed."""
        now = datetime(2026, 3, 1, 12, 0)
        engine.generate_alerts(53.35, -6.26, 'First', 70, timestamp=now)
        soon = now + timedelta(minutes=5)
        alerts = engine.generate_alerts(53.35, -6.26, 'Second', 70, timestamp=soon)
        assert len(alerts) == 0  # Both users in cooldown

    def test_cooldown_expires(self, engine):
        """Alerts should resume after the cooldown period expires."""
        now = datetime(2026, 3, 1, 12, 0)
        engine.generate_alerts(53.35, -6.26, 'First', 70, timestamp=now)
        later = now + timedelta(minutes=60)
        alerts = engine.generate_alerts(53.35, -6.26, 'Second', 70, timestamp=later)
        assert len(alerts) >= 1

    def test_set_cooldown(self, engine):
        """Changing cooldown should affect future alerts."""
        engine.set_cooldown(5)
        assert engine._cooldown_minutes == 5

    def test_get_alert_history(self, engine):
        """Alert history should contain all generated alerts."""
        engine.generate_alerts(53.35, -6.26, 'Test', 70)
        history = engine.get_alert_history()
        assert len(history) >= 1

    def test_get_alert_history_by_user(self, engine):
        """Filtered alert history should return only the specified user."""
        engine.generate_alerts(53.35, -6.26, 'Test', 70)
        history = engine.get_alert_history(user_id='u1')
        assert all(a['user_id'] == 'u1' for a in history)

    def test_alert_count_by_user(self, engine):
        """Should count alerts per user correctly."""
        engine.generate_alerts(53.35, -6.26, 'Test', 70)
        counts = engine.get_alert_count_by_user()
        assert counts.get('u1', 0) >= 1

    def test_clear_history(self, engine):
        """Clearing history should remove all records."""
        engine.generate_alerts(53.35, -6.26, 'Test', 70)
        engine.clear_history()
        assert len(engine.get_alert_history()) == 0

    def test_escalation_chain(self, engine):
        """Escalation contacts should be returned based on severity threshold."""
        chain = [
            {'level': 'patrol', 'contact': 'patrol@garda.ie', 'min_severity': 30},
            {'level': 'sergeant', 'contact': 'sgt@garda.ie', 'min_severity': 60},
            {'level': 'superintendent', 'contact': 'super@garda.ie', 'min_severity': 80},
        ]
        engine.set_escalation_chain('DCC-01', chain)
        contacts = engine.get_escalation_contacts('DCC-01', 65)
        assert len(contacts) == 2  # patrol and sergeant

    def test_calculate_alert_radius_high(self, engine):
        """High severity should produce a larger alert radius."""
        radius = engine.calculate_alert_radius(90)
        assert radius > engine._default_radius

    def test_calculate_alert_radius_low(self, engine):
        """Low severity should produce a smaller alert radius."""
        radius = engine.calculate_alert_radius(20)
        assert radius < engine._default_radius
