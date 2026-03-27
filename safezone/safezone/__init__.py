"""
SafeZone - A neighbourhood safety analysis and incident management library.
Provides tools for incident classification, zone management, alert generation,
trend analysis, and report generation for community safety applications.

Author: Adithya Reddy Madireddy
Version: 1.0.0
"""

from .incident_classifier import IncidentClassifier
from .zone_manager import ZoneManager
from .alert_engine import AlertEngine
from .trend_analyzer import TrendAnalyzer
from .report_generator import ReportGenerator

__version__ = '1.0.0'
__author__ = 'Adithya Reddy Madireddy'
__all__ = [
    'IncidentClassifier',
    'ZoneManager',
    'AlertEngine',
    'TrendAnalyzer',
    'ReportGenerator'
]
