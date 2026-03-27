"""
IncidentClassifier module for the SafeZone library.
Provides severity scoring, category auto-detection, priority calculation,
and urgency level assignment for neighbourhood safety incidents.
Author: Adithya Reddy Madireddy
"""

from datetime import datetime
import re


class IncidentClassifier:
    """
    Classifies safety incidents by severity, category, priority, and urgency.
    Uses configurable scoring rules based on incident type, time of day,
    location factors, and keyword analysis of descriptions.
    """

    # Category-to-base-severity mapping
    CATEGORY_SEVERITY = {
        'assault': 90,
        'robbery': 85,
        'burglary': 80,
        'theft': 65,
        'arson': 95,
        'vandalism': 45,
        'suspicious_activity': 40,
        'noise_complaint': 20,
        'parking': 15,
        'trespassing': 50,
        'drug_activity': 70,
        'harassment': 60,
        'fraud': 55,
        'other': 30
    }

    # Keywords that indicate higher severity
    HIGH_SEVERITY_KEYWORDS = [
        'weapon', 'gun', 'knife', 'fire', 'blood', 'injured',
        'emergency', 'attack', 'threatening', 'dangerous', 'armed'
    ]

    # Keywords that indicate lower severity
    LOW_SEVERITY_KEYWORDS = [
        'minor', 'small', 'slight', 'old', 'historical', 'resolved'
    ]

    # Urgency level boundaries
    URGENCY_LEVELS = {
        'critical': (80, 100),
        'high': (60, 79),
        'medium': (35, 59),
        'low': (0, 34)
    }

    def __init__(self):
        """Initialize the classifier with default configuration."""
        self._night_bonus = 15
        self._weekend_bonus = 10
        self._keyword_weight = 5
        self._custom_rules = []

    def classify_severity(self, category, description='', timestamp=None):
        """
        Calculate the overall severity score for an incident.
        Combines base category score with time-of-day modifiers
        and description keyword analysis.

        Args:
            category: The incident category string.
            description: The incident description text.
            timestamp: The datetime of the incident (defaults to now).
        Returns:
            Integer severity score between 0 and 100.
        """
        base_score = self.get_base_score(category)
        time_modifier = self.get_time_modifier(timestamp)
        keyword_modifier = self.analyze_keywords(description)
        custom_modifier = self._apply_custom_rules(category, description)

        total = base_score + time_modifier + keyword_modifier + custom_modifier
        return max(0, min(100, total))

    def get_base_score(self, category):
        """
        Get the base severity score for a given incident category.
        Returns a default score of 30 for unrecognized categories.
        """
        return self.CATEGORY_SEVERITY.get(category.lower(), 30)

    def get_time_modifier(self, timestamp=None):
        """
        Calculate the time-of-day severity modifier.
        Night-time incidents (22:00-05:00) receive a bonus as they
        are statistically more dangerous and harder to investigate.
        Weekend incidents also receive a slight bonus.
        """
        if timestamp is None:
            timestamp = datetime.now()
        modifier = 0
        hour = timestamp.hour
        if hour >= 22 or hour < 5:
            modifier += self._night_bonus
        weekday = timestamp.weekday()
        if weekday >= 5:  # Saturday or Sunday
            modifier += self._weekend_bonus
        return modifier

    def analyze_keywords(self, description):
        """
        Scan the description text for severity-affecting keywords.
        Returns a positive or negative modifier based on the keywords found.
        """
        if not description:
            return 0
        desc_lower = description.lower()
        modifier = 0
        for keyword in self.HIGH_SEVERITY_KEYWORDS:
            if keyword in desc_lower:
                modifier += self._keyword_weight
        for keyword in self.LOW_SEVERITY_KEYWORDS:
            if keyword in desc_lower:
                modifier -= self._keyword_weight
        return modifier

    def detect_category(self, description):
        """
        Automatically detect the most likely incident category from
        the description text using keyword matching patterns.

        Args:
            description: The free-text incident description.
        Returns:
            The detected category string.
        """
        desc_lower = description.lower()
        patterns = {
            'assault': r'\b(assault|attack|hit|punch|fight|beaten)\b',
            'robbery': r'\b(robbed|robbery|hold.?up|mugged|stick.?up)\b',
            'burglary': r'\b(burgl|break.?in|broke\s+into|forced\s+entry)\b',
            'theft': r'\b(stole|stolen|theft|shoplifting|pickpocket)\b',
            'arson': r'\b(arson|fire\s+set|burning|ignited|ablaze)\b',
            'vandalism': r'\b(vandal|graffiti|smash|broken\s+window|damage)\b',
            'suspicious_activity': r'\b(suspicious|lurking|loitering|strange|creeping)\b',
            'noise_complaint': r'\b(noise|loud|music|party|shouting)\b',
            'drug_activity': r'\b(drug|narcotic|dealing|substance)\b',
            'harassment': r'\b(harass|stalk|threaten|intimidat)\b',
            'trespassing': r'\b(trespass|unauthorized|unlawful\s+entry)\b',
            'fraud': r'\b(fraud|scam|counterfeit|identity\s+theft)\b',
        }
        best_match = 'other'
        best_count = 0
        for category, pattern in patterns.items():
            matches = re.findall(pattern, desc_lower)
            if len(matches) > best_count:
                best_count = len(matches)
                best_match = category
        return best_match

    def get_urgency_level(self, severity_score):
        """
        Map a numeric severity score to a named urgency level.

        Args:
            severity_score: Integer between 0 and 100.
        Returns:
            String: 'critical', 'high', 'medium', or 'low'.
        """
        for level, (low, high) in self.URGENCY_LEVELS.items():
            if low <= severity_score <= high:
                return level
        return 'medium'

    def calculate_priority(self, severity_score, incident_count_in_area=0, is_repeat=False):
        """
        Calculate the priority rank for an incident combining severity
        with contextual factors such as incident density in the area
        and whether it is a repeat event at the same location.

        Args:
            severity_score: The numeric severity (0-100).
            incident_count_in_area: Number of recent incidents nearby.
            is_repeat: Whether this is a repeat incident at the same location.
        Returns:
            Integer priority score (higher means more urgent).
        """
        priority = severity_score
        # Cluster bonus: more incidents in the area means higher priority
        if incident_count_in_area > 5:
            priority += 15
        elif incident_count_in_area > 2:
            priority += 8
        # Repeat incident bonus
        if is_repeat:
            priority += 10
        return max(0, min(100, priority))

    def should_auto_escalate(self, severity_score):
        """
        Determine whether an incident should be automatically escalated
        to authorities based on its severity score.
        Returns True for critical and high severity incidents.
        """
        return severity_score >= 60

    def add_custom_rule(self, category, modifier):
        """
        Add a custom scoring rule for a specific category.
        Custom rules are applied additively during classification.
        """
        self._custom_rules.append({'category': category.lower(), 'modifier': modifier})

    def _apply_custom_rules(self, category, description):
        """Apply all registered custom rules and return the combined modifier."""
        modifier = 0
        for rule in self._custom_rules:
            if rule['category'] == category.lower():
                modifier += rule['modifier']
        return modifier

    def classify_batch(self, incidents):
        """
        Classify a batch of incidents at once. Each incident should be
        a dictionary with at least 'category' and optionally 'description'
        and 'timestamp' keys.

        Returns:
            List of dictionaries with severity, urgency, and priority for each.
        """
        results = []
        for incident in incidents:
            score = self.classify_severity(
                incident.get('category', 'other'),
                incident.get('description', ''),
                incident.get('timestamp')
            )
            results.append({
                'severity_score': score,
                'urgency': self.get_urgency_level(score),
                'priority': self.calculate_priority(score),
                'auto_escalate': self.should_auto_escalate(score)
            })
        return results
