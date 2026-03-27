"""
ReportGenerator module for the SafeZone library.
Builds summary reports, aggregates incident data, produces statistics,
and exports in markdown and plain text formats.
Author: Adithya Reddy Madireddy
"""

from datetime import datetime
from collections import defaultdict


class ReportGenerator:
    """
    Generates structured reports from incident data including summary
    statistics, category breakdowns, zone-based aggregations, and
    time-based analysis. Supports markdown and plain text output.
    """

    def __init__(self, title='Safety Incident Report'):
        """
        Initialize the report generator with a report title.

        Args:
            title: The heading for generated reports.
        """
        self._title = title
        self._incidents = []
        self._zones = {}
        self._generated_at = None

    def set_title(self, title):
        """Update the report title."""
        self._title = title

    def add_incident(self, incident_id, title, category, severity, zone_id=None,
                     status='reported', timestamp=None):
        """
        Add an incident record to the report dataset.

        Args:
            incident_id: Unique identifier for the incident.
            title: Short incident title.
            category: Incident category string.
            severity: Numeric severity score (0-100).
            zone_id: Optional zone identifier.
            status: Current incident status.
            timestamp: When the incident occurred.
        """
        self._incidents.append({
            'id': incident_id,
            'title': title,
            'category': category,
            'severity': severity,
            'zone_id': zone_id,
            'status': status,
            'timestamp': timestamp or datetime.now()
        })

    def add_zone_info(self, zone_id, name, population=None):
        """Register a zone for zone-based report sections."""
        self._zones[zone_id] = {'name': name, 'population': population}

    def clear_data(self):
        """Clear all incident and zone data."""
        self._incidents.clear()
        self._zones.clear()

    def get_summary_statistics(self):
        """
        Calculate summary statistics for the current dataset.
        Returns a dictionary with total count, category breakdown,
        severity stats, and status breakdown.
        """
        if not self._incidents:
            return {'total': 0, 'message': 'No incidents to summarize.'}

        total = len(self._incidents)
        severities = [inc['severity'] for inc in self._incidents]
        avg_severity = sum(severities) / total
        max_severity = max(severities)
        min_severity = min(severities)

        by_category = defaultdict(int)
        for inc in self._incidents:
            by_category[inc['category']] += 1

        by_status = defaultdict(int)
        for inc in self._incidents:
            by_status[inc['status']] += 1

        return {
            'total': total,
            'avg_severity': round(avg_severity, 2),
            'max_severity': max_severity,
            'min_severity': min_severity,
            'by_category': dict(by_category),
            'by_status': dict(by_status)
        }

    def aggregate_by_category(self):
        """
        Aggregate incidents by category with count and average severity.
        Returns a sorted list of category summary dictionaries.
        """
        cat_data = defaultdict(lambda: {'count': 0, 'total_severity': 0})
        for inc in self._incidents:
            cat_data[inc['category']]['count'] += 1
            cat_data[inc['category']]['total_severity'] += inc['severity']

        result = []
        for cat, data in cat_data.items():
            result.append({
                'category': cat,
                'count': data['count'],
                'avg_severity': round(data['total_severity'] / data['count'], 2)
            })
        return sorted(result, key=lambda x: x['count'], reverse=True)

    def aggregate_by_zone(self):
        """
        Aggregate incidents by neighbourhood zone with count, average severity,
        and optional crime rate if population data is available.
        """
        zone_data = defaultdict(lambda: {'count': 0, 'total_severity': 0})
        for inc in self._incidents:
            zid = inc.get('zone_id')
            if zid:
                zone_data[zid]['count'] += 1
                zone_data[zid]['total_severity'] += inc['severity']

        result = []
        for zid, data in zone_data.items():
            entry = {
                'zone_id': zid,
                'zone_name': self._zones.get(zid, {}).get('name', zid),
                'count': data['count'],
                'avg_severity': round(data['total_severity'] / data['count'], 2)
            }
            pop = self._zones.get(zid, {}).get('population')
            if pop and pop > 0:
                entry['rate_per_1000'] = round((data['count'] / pop) * 1000, 4)
            result.append(entry)
        return sorted(result, key=lambda x: x['count'], reverse=True)

    def aggregate_by_time_period(self, period='day'):
        """
        Aggregate incidents by time period (day, week, or month).

        Args:
            period: One of 'day', 'week', or 'month'.
        Returns:
            Dictionary mapping period keys to incident counts.
        """
        aggregated = defaultdict(int)
        for inc in self._incidents:
            ts = inc['timestamp']
            if period == 'day':
                key = ts.strftime('%Y-%m-%d')
            elif period == 'week':
                key = f"{ts.year}-W{ts.isocalendar()[1]:02d}"
            elif period == 'month':
                key = ts.strftime('%Y-%m')
            else:
                key = ts.strftime('%Y-%m-%d')
            aggregated[key] += 1
        return dict(sorted(aggregated.items()))

    def get_top_incidents(self, n=5):
        """Return the top N incidents ranked by severity score."""
        sorted_inc = sorted(self._incidents, key=lambda x: x['severity'], reverse=True)
        return sorted_inc[:n]

    def generate_markdown_report(self):
        """
        Generate a complete report in Markdown format including title,
        generation timestamp, summary statistics, category breakdown,
        zone breakdown, and top incidents.
        """
        self._generated_at = datetime.now()
        stats = self.get_summary_statistics()
        lines = [
            f'# {self._title}',
            f'',
            f'Generated: {self._generated_at.strftime("%Y-%m-%d %H:%M:%S")}',
            f'',
            f'## Summary',
            f'',
            f'Total Incidents: {stats.get("total", 0)}',
            f'Average Severity: {stats.get("avg_severity", 0)}',
            f'Maximum Severity: {stats.get("max_severity", 0)}',
            f'Minimum Severity: {stats.get("min_severity", 0)}',
            f'',
        ]

        # Category breakdown section
        lines.append('## Incidents by Category')
        lines.append('')
        for entry in self.aggregate_by_category():
            lines.append(f'- {entry["category"]}: {entry["count"]} '
                         f'(avg severity: {entry["avg_severity"]})')
        lines.append('')

        # Zone breakdown section
        zone_agg = self.aggregate_by_zone()
        if zone_agg:
            lines.append('## Incidents by Zone')
            lines.append('')
            for entry in zone_agg:
                lines.append(f'- {entry["zone_name"]}: {entry["count"]} '
                             f'(avg severity: {entry["avg_severity"]})')
            lines.append('')

        # Top incidents
        lines.append('## Top Incidents by Severity')
        lines.append('')
        for inc in self.get_top_incidents():
            lines.append(f'- [{inc["severity"]}] {inc["title"]} ({inc["category"]})')
        lines.append('')

        return '\n'.join(lines)

    def generate_text_report(self):
        """
        Generate a complete report in plain text format.
        Uses simple formatting with separators and aligned columns.
        """
        self._generated_at = datetime.now()
        stats = self.get_summary_statistics()
        sep = '=' * 60

        lines = [
            sep,
            f'  {self._title.upper()}',
            sep,
            f'  Generated: {self._generated_at.strftime("%Y-%m-%d %H:%M:%S")}',
            '',
            f'  Total Incidents:   {stats.get("total", 0)}',
            f'  Average Severity:  {stats.get("avg_severity", 0)}',
            f'  Max Severity:      {stats.get("max_severity", 0)}',
            f'  Min Severity:      {stats.get("min_severity", 0)}',
            '',
            '-' * 60,
            '  CATEGORY BREAKDOWN',
            '-' * 60,
        ]
        for entry in self.aggregate_by_category():
            lines.append(f'  {entry["category"]:<25} {entry["count"]:>5}   '
                         f'(avg: {entry["avg_severity"]})')

        lines.append('')
        lines.append(sep)
        return '\n'.join(lines)

    def export_data(self):
        """
        Export all report data as a structured dictionary suitable
        for JSON serialization or further processing.
        """
        return {
            'title': self._title,
            'generated_at': datetime.now().isoformat(),
            'summary': self.get_summary_statistics(),
            'by_category': self.aggregate_by_category(),
            'by_zone': self.aggregate_by_zone(),
            'top_incidents': self.get_top_incidents(),
            'incident_count': len(self._incidents)
        }
