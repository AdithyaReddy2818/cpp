# SafeZone

A neighbourhood safety analysis and incident management library built for the Neighbourhood Safety Incident Reporting App.

## Features

- **IncidentClassifier**: Severity scoring, category auto-detection, priority calculation, and urgency level assignment.
- **ZoneManager**: Neighbourhood polygon boundaries, point-in-zone detection, proximity calculations, and hotspot identification.
- **AlertEngine**: Radius-based alerts, escalation chains, cool-down periods, and channel preferences.
- **TrendAnalyzer**: Moving averages, seasonal patterns, crime rate calculations, and spike detection.
- **ReportGenerator**: Summary statistics, incident aggregation, markdown and text report export.

## Installation

```bash
pip install -e .
```

## Usage

```python
from safezone import IncidentClassifier, ZoneManager, AlertEngine

classifier = IncidentClassifier()
score = classifier.classify_severity('theft', 'Bicycle stolen from park')
urgency = classifier.get_urgency_level(score)

zone_mgr = ZoneManager()
zone_mgr.add_zone('Z1', 'City Centre', [(53.34, -6.28), (53.36, -6.28), (53.36, -6.24), (53.34, -6.24)])
zone_id = zone_mgr.find_zone_for_point(53.35, -6.26)
```

## Testing

```bash
pytest tests/ -v
```

## Author

Adithya Reddy Madireddy - National College of Ireland
