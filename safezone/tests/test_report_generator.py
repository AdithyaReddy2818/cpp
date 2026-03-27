"""
Tests for the ReportGenerator class.
Author: Adithya Reddy Madireddy
"""

import pytest
from datetime import datetime, timedelta
from safezone.report_generator import ReportGenerator


@pytest.fixture
def generator():
    """Provide a ReportGenerator pre-loaded with sample incidents."""
    rg = ReportGenerator('Test Safety Report')
    rg.add_zone_info('DCC-01', 'Dublin City Centre', population=50000)
    rg.add_zone_info('DCC-02', 'Rathmines', population=15000)
    base = datetime(2026, 1, 1)
    incidents = [
        (1, 'Bike Theft', 'theft', 65, 'DCC-01', 'reported'),
        (2, 'Wall Graffiti', 'vandalism', 40, 'DCC-01', 'investigating'),
        (3, 'Mugging', 'robbery', 85, 'DCC-02', 'reported'),
        (4, 'Car Break-in', 'theft', 70, 'DCC-01', 'resolved'),
        (5, 'Window Smash', 'vandalism', 45, 'DCC-02', 'reported'),
        (6, 'Assault', 'assault', 90, 'DCC-01', 'investigating'),
        (7, 'Suspicious Person', 'suspicious_activity', 35, 'DCC-02', 'closed'),
        (8, 'Noise Late Night', 'noise_complaint', 20, 'DCC-01', 'resolved'),
    ]
    for i, (iid, title, cat, sev, zone, status) in enumerate(incidents):
        rg.add_incident(iid, title, cat, sev, zone, status,
                        base + timedelta(days=i))
    return rg


class TestReportGenerator:

    def test_set_title(self):
        """Setting title should update the report heading."""
        rg = ReportGenerator()
        rg.set_title('New Title')
        assert rg._title == 'New Title'

    def test_add_incident(self):
        """Adding incidents should increase the internal count."""
        rg = ReportGenerator()
        rg.add_incident(1, 'Test', 'theft', 50)
        assert len(rg._incidents) == 1

    def test_clear_data(self, generator):
        """Clearing data should remove all incidents and zones."""
        generator.clear_data()
        assert len(generator._incidents) == 0
        assert len(generator._zones) == 0

    def test_summary_statistics(self, generator):
        """Summary should include total, avg, max, and min severity."""
        stats = generator.get_summary_statistics()
        assert stats['total'] == 8
        assert stats['avg_severity'] > 0
        assert stats['max_severity'] == 90
        assert stats['min_severity'] == 20

    def test_summary_empty(self):
        """Empty dataset should return a zero-total summary."""
        rg = ReportGenerator()
        stats = rg.get_summary_statistics()
        assert stats['total'] == 0

    def test_aggregate_by_category(self, generator):
        """Category aggregation should return sorted results."""
        agg = generator.aggregate_by_category()
        assert len(agg) > 0
        categories = [a['category'] for a in agg]
        assert 'theft' in categories
        assert 'vandalism' in categories

    def test_aggregate_by_zone(self, generator):
        """Zone aggregation should include zone names and counts."""
        agg = generator.aggregate_by_zone()
        assert len(agg) == 2
        zone_names = [a['zone_name'] for a in agg]
        assert 'Dublin City Centre' in zone_names

    def test_aggregate_by_zone_with_rate(self, generator):
        """Zone aggregation should include per-1000 rate when population is set."""
        agg = generator.aggregate_by_zone()
        for entry in agg:
            assert 'rate_per_1000' in entry

    def test_aggregate_by_time_day(self, generator):
        """Time aggregation by day should return daily counts."""
        agg = generator.aggregate_by_time_period('day')
        assert isinstance(agg, dict)
        assert len(agg) > 0

    def test_aggregate_by_time_month(self, generator):
        """Time aggregation by month should return monthly counts."""
        agg = generator.aggregate_by_time_period('month')
        assert '2026-01' in agg

    def test_get_top_incidents(self, generator):
        """Top incidents should be sorted by severity descending."""
        top = generator.get_top_incidents(3)
        assert len(top) == 3
        assert top[0]['severity'] >= top[1]['severity']

    def test_generate_markdown_report(self, generator):
        """Markdown report should contain the title and summary sections."""
        md = generator.generate_markdown_report()
        assert '# Test Safety Report' in md
        assert '## Summary' in md
        assert '## Incidents by Category' in md

    def test_generate_text_report(self, generator):
        """Text report should contain the uppercase title and stats."""
        txt = generator.generate_text_report()
        assert 'TEST SAFETY REPORT' in txt
        assert 'Total Incidents' in txt

    def test_export_data(self, generator):
        """Exported data should be a serializable dictionary."""
        data = generator.export_data()
        assert 'title' in data
        assert 'summary' in data
        assert data['incident_count'] == 8
