"""Incident classification and severity analysis."""

import re
from datetime import datetime, timezone


class IncidentClassifier:
    """Classifies safety incidents by category, severity, and priority."""

    KEYWORD_MAP = {
        "theft": [
            "stolen", "robbery", "robbed", "theft", "burglar", "burglary",
            "shoplifting", "pickpocket", "mugging", "break-in", "broke in",
            "larceny", "stealing", "stole",
        ],
        "vandalism": [
            "graffiti", "damage", "damaged", "vandalism", "vandalized",
            "smashed", "broken window", "defaced", "spray paint", "keyed",
            "slashed tires", "property destruction",
        ],
        "suspicious_activity": [
            "suspicious", "loitering", "lurking", "prowler", "trespassing",
            "peeping", "stalking", "stranger", "unknown person", "casing",
            "watching", "following",
        ],
        "accident": [
            "accident", "crash", "collision", "hit and run", "hit-and-run",
            "injured", "injury", "fell", "slip", "trip", "pothole",
        ],
        "noise_complaint": [
            "noise", "loud", "music", "party", "barking", "shouting",
            "yelling", "disturbance", "fireworks", "honking",
        ],
        "fire": [
            "fire", "smoke", "burning", "flames", "arson", "blaze",
            "combustion", "ignited",
        ],
        "flooding": [
            "flood", "flooding", "water damage", "burst pipe", "overflow",
            "waterlogged", "submerged", "leak", "leaking",
        ],
        "assault": [
            "assault", "attacked", "attack", "fight", "fighting", "punched",
            "stabbed", "beaten", "threatened", "weapon", "harassment",
            "violent", "violence",
        ],
    }

    SEVERITY_MAP = {
        "assault": "critical",
        "fire": "critical",
        "theft": "high",
        "accident": "high",
        "flooding": "high",
        "vandalism": "medium",
        "suspicious_activity": "medium",
        "noise_complaint": "low",
        "other": "low",
    }

    SEVERITY_SCORES = {
        "critical": 9,
        "high": 7,
        "medium": 5,
        "low": 3,
    }

    SAFETY_KEYWORDS = [
        "danger", "emergency", "urgent", "help", "police", "ambulance",
        "fire department", "threat", "unsafe", "hazard", "warning",
        "caution", "risk", "alarm", "crime", "victim", "witness",
        "suspect", "weapon", "injury", "blood", "911", "999",
    ]

    def classify_incident(self, description: str) -> str:
        """Classify an incident description into a category.

        Scans the description for keywords and returns the best-matching
        category from the predefined list.

        Args:
            description: Free-text incident description.

        Returns:
            One of: 'theft', 'vandalism', 'suspicious_activity', 'accident',
            'noise_complaint', 'fire', 'flooding', 'assault', 'other'.
        """
        if not description:
            return "other"

        text = description.lower()
        scores = {}

        for category, keywords in self.KEYWORD_MAP.items():
            count = 0
            for kw in keywords:
                if kw in text:
                    count += 1
            if count > 0:
                scores[category] = count

        if not scores:
            return "other"

        return max(scores, key=scores.get)

    def get_severity_level(self, incident_type: str) -> str:
        """Return severity level for a given incident type.

        Args:
            incident_type: The classified category string.

        Returns:
            One of: 'critical', 'high', 'medium', 'low'.
        """
        return self.SEVERITY_MAP.get(incident_type, "low")

    def get_priority_score(self, incident: dict) -> int:
        """Calculate a priority score from 1 to 10 for an incident.

        Score is based on severity of the incident type plus a recency
        bonus (incidents within the last 24 hours score higher).

        Args:
            incident: Dict with at least 'type' key, optionally 'created_at'
                      (ISO-format string or datetime).

        Returns:
            Integer score between 1 and 10.
        """
        incident_type = incident.get("type", "other")
        severity = self.get_severity_level(incident_type)
        base = self.SEVERITY_SCORES.get(severity, 3)

        created_at = incident.get("created_at")
        recency_bonus = 0
        if created_at:
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    created_at = None
            if isinstance(created_at, datetime):
                now = datetime.now(timezone.utc)
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                hours_ago = (now - created_at).total_seconds() / 3600
                if hours_ago <= 1:
                    recency_bonus = 1
                elif hours_ago <= 6:
                    recency_bonus = 0.5

        score = round(base + recency_bonus)
        return max(1, min(10, score))

    def extract_keywords(self, text: str) -> list:
        """Extract safety-related keywords found in the text.

        Args:
            text: Free-text string to scan.

        Returns:
            Sorted list of unique safety keywords found.
        """
        if not text:
            return []

        lower = text.lower()
        found = set()

        for kw in self.SAFETY_KEYWORDS:
            if kw in lower:
                found.add(kw)

        for category, keywords in self.KEYWORD_MAP.items():
            for kw in keywords:
                if kw in lower:
                    found.add(kw)

        return sorted(found)
