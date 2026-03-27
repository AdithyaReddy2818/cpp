"""Unit tests for the incident_lib library."""

import unittest
from datetime import datetime, timedelta, timezone

from incident_lib.classifier import IncidentClassifier
from incident_lib.validator import ReportValidator
from incident_lib.analytics import SafetyAnalytics
from incident_lib.formatter import IncidentFormatter


class TestIncidentClassifier(unittest.TestCase):

    def setUp(self):
        self.clf = IncidentClassifier()

    # --- classify_incident ---

    def test_classify_theft(self):
        self.assertEqual(self.clf.classify_incident("My bike was stolen from the rack"), "theft")

    def test_classify_theft_robbery(self):
        self.assertEqual(self.clf.classify_incident("There was a robbery at the shop"), "theft")

    def test_classify_vandalism(self):
        self.assertEqual(self.clf.classify_incident("Graffiti on the wall and damage to fence"), "vandalism")

    def test_classify_assault(self):
        self.assertEqual(self.clf.classify_incident("A person was attacked with a weapon"), "assault")

    def test_classify_fire(self):
        self.assertEqual(self.clf.classify_incident("Smoke and flames coming from the building"), "fire")

    def test_classify_noise(self):
        self.assertEqual(self.clf.classify_incident("Loud music playing all night party"), "noise_complaint")

    def test_classify_suspicious(self):
        self.assertEqual(self.clf.classify_incident("Suspicious person loitering near school"), "suspicious_activity")

    def test_classify_accident(self):
        self.assertEqual(self.clf.classify_incident("Car crash at the intersection, injured driver"), "accident")

    def test_classify_flooding(self):
        self.assertEqual(self.clf.classify_incident("Burst pipe causing flooding in the basement"), "flooding")

    def test_classify_other(self):
        self.assertEqual(self.clf.classify_incident("Something happened today"), "other")

    def test_classify_empty(self):
        self.assertEqual(self.clf.classify_incident(""), "other")

    # --- get_severity_level ---

    def test_severity_critical_assault(self):
        self.assertEqual(self.clf.get_severity_level("assault"), "critical")

    def test_severity_critical_fire(self):
        self.assertEqual(self.clf.get_severity_level("fire"), "critical")

    def test_severity_high_theft(self):
        self.assertEqual(self.clf.get_severity_level("theft"), "high")

    def test_severity_medium_vandalism(self):
        self.assertEqual(self.clf.get_severity_level("vandalism"), "medium")

    def test_severity_low_noise(self):
        self.assertEqual(self.clf.get_severity_level("noise_complaint"), "low")

    def test_severity_low_other(self):
        self.assertEqual(self.clf.get_severity_level("other"), "low")

    # --- get_priority_score ---

    def test_priority_assault(self):
        score = self.clf.get_priority_score({"type": "assault"})
        self.assertGreaterEqual(score, 8)

    def test_priority_noise(self):
        score = self.clf.get_priority_score({"type": "noise_complaint"})
        self.assertLessEqual(score, 4)

    def test_priority_recent_bonus(self):
        recent = datetime.now(timezone.utc) - timedelta(minutes=30)
        score = self.clf.get_priority_score({"type": "theft", "created_at": recent})
        self.assertGreaterEqual(score, 7)

    # --- extract_keywords ---

    def test_extract_keywords(self):
        kws = self.clf.extract_keywords("A stolen bike, police called for emergency help")
        self.assertIn("stolen", kws)
        self.assertIn("police", kws)
        self.assertIn("emergency", kws)

    def test_extract_keywords_empty(self):
        self.assertEqual(self.clf.extract_keywords(""), [])


class TestReportValidator(unittest.TestCase):

    def setUp(self):
        self.val = ReportValidator()

    def test_valid_report(self):
        data = {
            "title": "Broken window on Main St",
            "description": "Window smashed at shop front around 10pm last night",
            "category": "vandalism",
            "location": "Main Street",
        }
        valid, errors = self.val.validate_report(data)
        self.assertTrue(valid)
        self.assertEqual(errors, [])

    def test_report_missing_title(self):
        data = {"description": "Something happened here", "location": "Park Ave"}
        valid, errors = self.val.validate_report(data)
        self.assertFalse(valid)
        self.assertTrue(any("Title" in e for e in errors))

    def test_report_short_description(self):
        data = {"title": "Test Title", "description": "Short", "location": "Elm St"}
        valid, errors = self.val.validate_report(data)
        self.assertFalse(valid)

    def test_report_invalid_category(self):
        data = {
            "title": "Test Title",
            "description": "A valid long description for testing",
            "category": "alien_invasion",
            "location": "Elm St",
        }
        valid, errors = self.val.validate_report(data)
        self.assertFalse(valid)
        self.assertTrue(any("category" in e.lower() for e in errors))

    def test_valid_user(self):
        data = {"username": "adithya", "email": "a@test.com", "password": "Secure1pass"}
        valid, errors = self.val.validate_user(data)
        self.assertTrue(valid)

    def test_user_short_username(self):
        data = {"username": "ab", "email": "a@b.com", "password": "Secure1pass"}
        valid, errors = self.val.validate_user(data)
        self.assertFalse(valid)

    def test_user_bad_email(self):
        data = {"username": "adithya", "email": "notemail", "password": "Secure1pass"}
        valid, errors = self.val.validate_user(data)
        self.assertFalse(valid)

    def test_user_weak_password(self):
        data = {"username": "adithya", "email": "a@b.com", "password": "short"}
        valid, errors = self.val.validate_user(data)
        self.assertFalse(valid)

    def test_sanitize_input(self):
        result = self.val.sanitize_input("<script>alert('xss')</script>Hello")
        self.assertEqual(result, "alert('xss')Hello")

    def test_sanitize_empty(self):
        self.assertEqual(self.val.sanitize_input(""), "")

    def test_valid_coordinates(self):
        valid, errors = self.val.validate_coordinates(53.3498, -6.2603)
        self.assertTrue(valid)

    def test_invalid_latitude(self):
        valid, errors = self.val.validate_coordinates(100, 0)
        self.assertFalse(valid)

    def test_invalid_longitude(self):
        valid, errors = self.val.validate_coordinates(0, 200)
        self.assertFalse(valid)


class TestSafetyAnalytics(unittest.TestCase):

    def setUp(self):
        self.analytics = SafetyAnalytics()
        now = datetime.now(timezone.utc)
        self.incidents = [
            {"type": "theft", "severity": "high", "status": "open",
             "created_at": now - timedelta(hours=2), "latitude": 53.35, "longitude": -6.26},
            {"type": "theft", "severity": "high", "status": "resolved",
             "created_at": now - timedelta(hours=10), "latitude": 53.35, "longitude": -6.26},
            {"type": "vandalism", "severity": "medium", "status": "open",
             "created_at": now - timedelta(days=2), "latitude": 53.36, "longitude": -6.27},
            {"type": "assault", "severity": "critical", "status": "open",
             "created_at": now - timedelta(hours=5), "latitude": 53.35, "longitude": -6.26},
        ]

    def test_stats_total(self):
        stats = self.analytics.get_incident_stats(self.incidents)
        self.assertEqual(stats["total"], 4)

    def test_stats_by_category(self):
        stats = self.analytics.get_incident_stats(self.incidents)
        self.assertEqual(stats["by_category"]["theft"], 2)

    def test_stats_by_severity(self):
        stats = self.analytics.get_incident_stats(self.incidents)
        self.assertEqual(stats["by_severity"]["high"], 2)

    def test_hotspots(self):
        hotspots = self.analytics.get_hotspot_areas(self.incidents)
        self.assertGreater(len(hotspots), 0)
        self.assertGreaterEqual(hotspots[0]["count"], 2)

    def test_trend_data(self):
        trend = self.analytics.get_trend_data(self.incidents, days=7)
        self.assertEqual(len(trend), 7)
        total = sum(d["count"] for d in trend)
        self.assertGreater(total, 0)

    def test_recent_incidents(self):
        recent = self.analytics.get_recent_incidents(self.incidents, hours=6)
        self.assertGreaterEqual(len(recent), 1)

    def test_recent_incidents_narrow(self):
        recent = self.analytics.get_recent_incidents(self.incidents, hours=1)
        self.assertEqual(len(recent), 0)

    def test_safety_report(self):
        report = self.analytics.generate_safety_report(self.incidents, "Dublin 1")
        self.assertIn("Dublin 1", report)
        self.assertIn("Total Incidents: 4", report)

    def test_empty_stats(self):
        stats = self.analytics.get_incident_stats([])
        self.assertEqual(stats["total"], 0)


class TestIncidentFormatter(unittest.TestCase):

    def setUp(self):
        self.fmt = IncidentFormatter()
        self.incident = {
            "id": "INC-001",
            "title": "Bike Theft",
            "type": "theft",
            "severity": "high",
            "status": "open",
            "location": "Main St",
            "description": "Mountain bike stolen from rack outside shop.",
            "created_at": "2026-03-28 14:00",
            "reported_by": "Adithya",
        }

    def test_summary_format(self):
        s = self.fmt.format_incident_summary(self.incident)
        self.assertIn("[HIGH]", s)
        self.assertIn("theft", s)
        self.assertIn("Bike Theft", s)
        self.assertIn("Main St", s)

    def test_detail_format(self):
        d = self.fmt.format_incident_detail(self.incident)
        self.assertIn("INC-001", d)
        self.assertIn("Adithya", d)
        self.assertIn("Mountain bike", d)

    def test_csv_output(self):
        csv_text = self.fmt.to_csv([self.incident])
        self.assertIn("id,title,category", csv_text)
        self.assertIn("INC-001", csv_text)
        self.assertIn("Bike Theft", csv_text)

    def test_csv_empty(self):
        csv_text = self.fmt.to_csv([])
        self.assertIn("id,title,category", csv_text)

    def test_alert_format(self):
        alert = self.fmt.format_alert(self.incident)
        self.assertIn("SAFETY ALERT", alert)
        self.assertIn("[HIGH]", alert)
        self.assertIn("Main St", alert)

    def test_stats_dashboard(self):
        stats = {
            "total": 4,
            "by_category": {"theft": 2, "vandalism": 1, "assault": 1},
            "by_severity": {"high": 2, "medium": 1, "critical": 1},
            "by_status": {"open": 3, "resolved": 1},
        }
        dashboard = self.fmt.format_stats_dashboard(stats)
        self.assertIn("SAFETY STATS DASHBOARD", dashboard)
        self.assertIn("theft", dashboard)


if __name__ == "__main__":
    unittest.main()
