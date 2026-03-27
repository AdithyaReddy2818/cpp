"""
TrendAnalyzer module for the SafeZone library.
Provides time-series analysis, seasonal pattern detection, crime rate
calculations, zone comparison, and spike detection for incident data.
Author: Adithya Reddy Madireddy
"""

from datetime import datetime, timedelta
from collections import defaultdict
import math


class TrendAnalyzer:
    """
    Analyses incident data over time to identify trends, seasonal patterns,
    and anomalies in neighbourhood safety. Supports moving averages,
    rate calculations, zone comparisons, and statistical spike detection.
    """

    def __init__(self):
        """Initialize the trend analyzer with an empty incident dataset."""
        self._incidents = []

    def add_incident(self, timestamp, category, zone_id=None, severity=50):
        """
        Add an incident record to the dataset for analysis.

        Args:
            timestamp: The datetime when the incident occurred.
            category: The incident category string.
            zone_id: Optional zone identifier for zone-based analysis.
            severity: Numeric severity score (0-100).
        """
        self._incidents.append({
            'timestamp': timestamp,
            'category': category,
            'zone_id': zone_id,
            'severity': severity
        })

    def clear_data(self):
        """Remove all incident data from the analyzer."""
        self._incidents.clear()

    def get_incident_count(self):
        """Return the total number of incidents in the dataset."""
        return len(self._incidents)

    def incidents_per_day(self, start_date=None, end_date=None):
        """
        Calculate daily incident counts within an optional date range.

        Returns:
            Dictionary mapping date strings (YYYY-MM-DD) to counts.
        """
        filtered = self._filter_by_date(start_date, end_date)
        daily = defaultdict(int)
        for inc in filtered:
            day_key = inc['timestamp'].strftime('%Y-%m-%d')
            daily[day_key] += 1
        return dict(sorted(daily.items()))

    def moving_average(self, window_days=7, start_date=None, end_date=None):
        """
        Calculate a simple moving average of daily incident counts.

        Args:
            window_days: The number of days in the moving average window.
            start_date: Optional start of the analysis period.
            end_date: Optional end of the analysis period.
        Returns:
            List of (date_string, average_value) tuples.
        """
        daily = self.incidents_per_day(start_date, end_date)
        if not daily:
            return []

        dates = sorted(daily.keys())
        values = [daily[d] for d in dates]
        averages = []

        for i in range(len(values)):
            window_start = max(0, i - window_days + 1)
            window = values[window_start:i + 1]
            avg = sum(window) / len(window)
            averages.append((dates[i], round(avg, 2)))

        return averages

    def seasonal_pattern(self):
        """
        Detect seasonal patterns by aggregating incidents by month.
        Returns a dictionary mapping month numbers (1-12) to average
        daily incident counts for that month across all years.
        """
        monthly = defaultdict(list)
        daily = self.incidents_per_day()

        for date_str, count in daily.items():
            month = int(date_str.split('-')[1])
            monthly[month].append(count)

        pattern = {}
        for month, counts in monthly.items():
            pattern[month] = round(sum(counts) / len(counts), 2) if counts else 0

        return dict(sorted(pattern.items()))

    def hourly_distribution(self):
        """
        Analyse the distribution of incidents across hours of the day.
        Returns a dictionary mapping hour (0-23) to incident count.
        """
        hourly = defaultdict(int)
        for inc in self._incidents:
            hourly[inc['timestamp'].hour] += 1
        return dict(sorted(hourly.items()))

    def crime_rate(self, population, period_days=30):
        """
        Calculate the crime rate per 1000 residents over a given period.
        Uses only incidents within the most recent period_days.

        Args:
            population: The total population of the area.
            period_days: The number of days to consider.
        Returns:
            Crime rate as a float (incidents per 1000 people).
        """
        if population <= 0:
            raise ValueError("Population must be a positive number.")
        cutoff = datetime.now() - timedelta(days=period_days)
        recent = [inc for inc in self._incidents if inc['timestamp'] >= cutoff]
        rate = (len(recent) / population) * 1000
        return round(rate, 4)

    def compare_zones(self):
        """
        Compare incident counts and average severity across all zones.
        Returns a dictionary mapping zone_id to statistics.
        """
        zone_data = defaultdict(lambda: {'count': 0, 'total_severity': 0})
        for inc in self._incidents:
            zid = inc.get('zone_id')
            if zid:
                zone_data[zid]['count'] += 1
                zone_data[zid]['total_severity'] += inc['severity']

        result = {}
        for zid, data in zone_data.items():
            result[zid] = {
                'incident_count': data['count'],
                'avg_severity': round(data['total_severity'] / data['count'], 2)
            }
        return result

    def category_breakdown(self, start_date=None, end_date=None):
        """
        Break down incidents by category within an optional date range.
        Returns a dictionary mapping category to incident count.
        """
        filtered = self._filter_by_date(start_date, end_date)
        breakdown = defaultdict(int)
        for inc in filtered:
            breakdown[inc['category']] += 1
        return dict(sorted(breakdown.items(), key=lambda x: x[1], reverse=True))

    def detect_spikes(self, threshold_multiplier=2.0, window_days=7):
        """
        Detect days where incident counts exceed a threshold above the
        moving average, indicating unusual spikes in activity.

        Args:
            threshold_multiplier: How many times the average a day's count
                                  must exceed to be flagged as a spike.
            window_days: The moving average window size.
        Returns:
            List of (date_string, count, average) tuples for spike days.
        """
        ma = self.moving_average(window_days)
        daily = self.incidents_per_day()
        spikes = []

        for date_str, avg in ma:
            count = daily.get(date_str, 0)
            if avg > 0 and count >= avg * threshold_multiplier:
                spikes.append((date_str, count, avg))

        return spikes

    def severity_trend(self, window_days=7):
        """
        Track how average severity changes over time using a moving average.
        Returns a list of (date_string, average_severity) tuples.
        """
        daily_sev = defaultdict(list)
        for inc in self._incidents:
            day_key = inc['timestamp'].strftime('%Y-%m-%d')
            daily_sev[day_key].append(inc['severity'])

        dates = sorted(daily_sev.keys())
        daily_avg = [sum(daily_sev[d]) / len(daily_sev[d]) for d in dates]
        result = []

        for i in range(len(daily_avg)):
            window_start = max(0, i - window_days + 1)
            window = daily_avg[window_start:i + 1]
            avg = sum(window) / len(window)
            result.append((dates[i], round(avg, 2)))

        return result

    def _filter_by_date(self, start_date=None, end_date=None):
        """Filter the incident list by an optional date range."""
        filtered = self._incidents
        if start_date:
            filtered = [inc for inc in filtered if inc['timestamp'] >= start_date]
        if end_date:
            filtered = [inc for inc in filtered if inc['timestamp'] <= end_date]
        return filtered
