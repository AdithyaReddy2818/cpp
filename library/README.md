# incident-analysis-nci

A Python library for classifying, validating, analysing, and formatting neighbourhood safety incident reports.

**Author:** Adithya Reddy
**Version:** 1.0.0

## Installation

```bash
pip install incident-analysis-nci
```

Or install from source:

```bash
pip install -e .
```

## Features

- **IncidentClassifier** — Classify incidents by type, severity, and priority using keyword matching
- **ReportValidator** — Validate and sanitise incident reports and user data
- **SafetyAnalytics** — Generate statistics, hotspot maps, trend data, and safety reports
- **IncidentFormatter** — Format incidents for display, CSV export, and SNS alert notifications

## Quick Start

```python
from incident_lib import IncidentClassifier, ReportValidator, SafetyAnalytics, IncidentFormatter

# Classify an incident
clf = IncidentClassifier()
category = clf.classify_incident("Someone stole my bike from the rack")
print(category)  # "theft"
print(clf.get_severity_level(category))  # "high"

# Validate a report
val = ReportValidator()
valid, errors = val.validate_report({
    "title": "Bike stolen on Main St",
    "description": "My mountain bike was stolen from outside the shop at 10pm.",
    "category": "theft",
    "location": "Main Street",
})
print(valid)  # True

# Analytics
analytics = SafetyAnalytics()
stats = analytics.get_incident_stats(incidents)
hotspots = analytics.get_hotspot_areas(incidents)
report = analytics.generate_safety_report(incidents, "Dublin 1")

# Formatting
fmt = IncidentFormatter()
print(fmt.format_incident_summary(incident))
print(fmt.to_csv(incidents))
print(fmt.format_alert(incident))
```

## Dependencies

None — uses Python standard library only (`re`, `datetime`, `csv`, `io`, `collections`, `math`).

## Running Tests

```bash
python -m pytest tests/ -v
```

Or with unittest:

```bash
python -m unittest discover tests -v
```

## Incident Categories

| Category             | Severity |
|----------------------|----------|
| assault              | critical |
| fire                 | critical |
| theft                | high     |
| accident             | high     |
| flooding             | high     |
| vandalism            | medium   |
| suspicious_activity  | medium   |
| noise_complaint      | low      |
| other                | low      |

## License

MIT
