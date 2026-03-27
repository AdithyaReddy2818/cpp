"""
Tests for the IncidentClassifier class.
Author: Adithya Reddy Madireddy
"""

import pytest
from datetime import datetime
from safezone.incident_classifier import IncidentClassifier


@pytest.fixture
def classifier():
    """Provide a fresh IncidentClassifier instance for each test."""
    return IncidentClassifier()


class TestIncidentClassifier:

    def test_base_score_assault(self, classifier):
        """Assault should have a high base severity score."""
        assert classifier.get_base_score('assault') == 90

    def test_base_score_noise(self, classifier):
        """Noise complaints should have a low base severity score."""
        assert classifier.get_base_score('noise_complaint') == 20

    def test_base_score_unknown(self, classifier):
        """Unknown categories should return the default base score."""
        assert classifier.get_base_score('unknown_category') == 30

    def test_night_time_modifier(self, classifier):
        """Incidents at night should receive a positive time modifier."""
        night = datetime(2026, 1, 15, 23, 30)
        modifier = classifier.get_time_modifier(night)
        assert modifier > 0

    def test_daytime_modifier(self, classifier):
        """Incidents during daytime on weekdays should have zero modifier."""
        day = datetime(2026, 1, 12, 14, 0)  # Monday afternoon
        modifier = classifier.get_time_modifier(day)
        assert modifier == 0

    def test_weekend_modifier(self, classifier):
        """Weekend incidents should receive a positive modifier."""
        saturday = datetime(2026, 1, 17, 10, 0)  # Saturday
        modifier = classifier.get_time_modifier(saturday)
        assert modifier >= 10

    def test_keyword_analysis_high(self, classifier):
        """Descriptions with danger keywords should increase severity."""
        desc = 'The suspect was armed with a weapon and threatening people.'
        modifier = classifier.analyze_keywords(desc)
        assert modifier > 0

    def test_keyword_analysis_low(self, classifier):
        """Descriptions with minor keywords should decrease severity."""
        desc = 'A minor issue that has already been resolved.'
        modifier = classifier.analyze_keywords(desc)
        assert modifier < 0

    def test_keyword_analysis_empty(self, classifier):
        """Empty descriptions should return zero modifier."""
        assert classifier.analyze_keywords('') == 0

    def test_classify_severity_range(self, classifier):
        """Severity score should always be between 0 and 100."""
        score = classifier.classify_severity('assault', 'armed attack with weapon')
        assert 0 <= score <= 100

    def test_detect_category_theft(self, classifier):
        """Should detect theft from description keywords."""
        desc = 'Someone stole my bicycle from outside the shop.'
        assert classifier.detect_category(desc) == 'theft'

    def test_detect_category_vandalism(self, classifier):
        """Should detect vandalism from description keywords."""
        desc = 'Graffiti sprayed on the wall and a broken window.'
        assert classifier.detect_category(desc) == 'vandalism'

    def test_urgency_level_critical(self, classifier):
        """Score of 85 should map to critical urgency."""
        assert classifier.get_urgency_level(85) == 'critical'

    def test_urgency_level_low(self, classifier):
        """Score of 20 should map to low urgency."""
        assert classifier.get_urgency_level(20) == 'low'

    def test_priority_with_cluster(self, classifier):
        """Priority should increase when there are many incidents nearby."""
        base = classifier.calculate_priority(50, incident_count_in_area=10)
        solo = classifier.calculate_priority(50, incident_count_in_area=0)
        assert base > solo

    def test_auto_escalate_high(self, classifier):
        """High severity should trigger auto-escalation."""
        assert classifier.should_auto_escalate(75) is True

    def test_auto_escalate_low(self, classifier):
        """Low severity should not trigger auto-escalation."""
        assert classifier.should_auto_escalate(30) is False

    def test_custom_rule(self, classifier):
        """Custom rules should modify the severity score."""
        classifier.add_custom_rule('vandalism', 20)
        score_with = classifier.classify_severity('vandalism')
        classifier._custom_rules.clear()
        score_without = classifier.classify_severity('vandalism')
        assert score_with > score_without

    def test_classify_batch(self, classifier):
        """Batch classification should return results for all incidents."""
        incidents = [
            {'category': 'theft', 'description': 'Stolen phone'},
            {'category': 'assault', 'description': 'Attack in park'},
        ]
        results = classifier.classify_batch(incidents)
        assert len(results) == 2
        assert all('severity_score' in r for r in results)
