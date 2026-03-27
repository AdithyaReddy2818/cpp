"""
Tests for the TrendAnalyzer class.
Author: Adithya Reddy Madireddy
"""

import pytest
from datetime import datetime, timedelta
from safezone.trend_analyzer import TrendAnalyzer


@pytest.fixture
def analyzer():
    """Provide a TrendAnalyzer pre-loaded with sample data spanning 30 days."""
    ta = TrendAnalyzer()
    base = datetime(2026, 1, 1, 10, 0)
    categories = ['theft', 'vandalism', 'suspicious_activity', 'assault']
    zones = ['DCC-01', 'DCC-02']
    for i in range(60):
        ta.add_incident(
            timestamp=base + timedelta(days=i % 30, hours=i % 24),
            category=categories[i % len(categories)],
            zone_id=zones[i % len(zones)],
            severity=30 + (i * 7) % 70
        )
    return ta


class TestTrendAnalyzer:

    def test_add_incident(self):
        """Adding incidents should increase the count."""
        ta = TrendAnalyzer()
        ta.add_incident(datetime.now(), 'theft')
        assert ta.get_incident_count() == 1

    def test_clear_data(self, analyzer):
        """Clearing data should reset the count to zero."""
        analyzer.clear_data()
        assert analyzer.get_incident_count() == 0

    def test_incidents_per_day(self, analyzer):
        """Should return a dictionary of daily counts."""
        daily = analyzer.incidents_per_day()
        assert isinstance(daily, dict)
        assert len(daily) > 0
        assert all(isinstance(v, int) for v in daily.values())

    def test_incidents_per_day_filtered(self, analyzer):
        """Should filter by date range correctly."""
        start = datetime(2026, 1, 5)
        end = datetime(2026, 1, 10)
        daily = analyzer.incidents_per_day(start, end)
        for d in daily:
            assert '2026-01-05' <= d <= '2026-01-10'

    def test_moving_average(self, analyzer):
        """Moving average should return a list of date-value tuples."""
        ma = analyzer.moving_average(window_days=7)
        assert len(ma) > 0
        assert all(len(item) == 2 for item in ma)

    def test_seasonal_pattern(self, analyzer):
        """Seasonal pattern should return month-keyed dictionary."""
        pattern = analyzer.seasonal_pattern()
        assert isinstance(pattern, dict)
        assert all(1 <= m <= 12 for m in pattern.keys())

    def test_hourly_distribution(self, analyzer):
        """Hourly distribution should have entries for active hours."""
        hourly = analyzer.hourly_distribution()
        assert isinstance(hourly, dict)
        assert sum(hourly.values()) == analyzer.get_incident_count()

    def test_crime_rate(self, analyzer):
        """Crime rate should be a positive number per 1000 residents."""
        rate = analyzer.crime_rate(population=50000, period_days=365)
        assert rate >= 0

    def test_crime_rate_invalid_population(self, analyzer):
        """Zero population should raise ValueError."""
        with pytest.raises(ValueError):
            analyzer.crime_rate(population=0)

    def test_compare_zones(self, analyzer):
        """Zone comparison should return data for each zone with incidents."""
        comparison = analyzer.compare_zones()
        assert 'DCC-01' in comparison
        assert 'DCC-02' in comparison
        assert comparison['DCC-01']['incident_count'] > 0

    def test_category_breakdown(self, analyzer):
        """Category breakdown should return counts per category."""
        breakdown = analyzer.category_breakdown()
        assert 'theft' in breakdown
        assert breakdown['theft'] > 0

    def test_detect_spikes_no_spikes(self):
        """Uniform data should not produce spikes."""
        ta = TrendAnalyzer()
        base = datetime(2026, 1, 1)
        for i in range(30):
            ta.add_incident(base + timedelta(days=i), 'theft', severity=50)
        spikes = ta.detect_spikes(threshold_multiplier=3.0)
        assert len(spikes) == 0

    def test_detect_spikes_with_spike(self):
        """A day with many incidents should be detected as a spike."""
        ta = TrendAnalyzer()
        base = datetime(2026, 1, 1)
        for i in range(30):
            ta.add_incident(base + timedelta(days=i), 'theft', severity=50)
        # Add a big spike on day 15
        spike_day = base + timedelta(days=15)
        for _ in range(20):
            ta.add_incident(spike_day, 'theft', severity=50)
        spikes = ta.detect_spikes(threshold_multiplier=2.0)
        assert len(spikes) >= 1

    def test_severity_trend(self, analyzer):
        """Severity trend should return date-severity tuples."""
        trend = analyzer.severity_trend(window_days=7)
        assert len(trend) > 0
        assert all(len(t) == 2 for t in trend)
