"""Formatting utilities for incident reports, alerts, and dashboards."""

import csv
import io


class IncidentFormatter:
    """Formats incident data for display, export, and notifications."""

    def format_incident_summary(self, incident: dict) -> str:
        """Format an incident as a single-line summary.

        Format: [SEVERITY] Category - Title (Location) - Date

        Args:
            incident: Dict with keys: severity, type/category, title,
                      location, created_at.

        Returns:
            One-line summary string.
        """
        severity = incident.get("severity", "unknown").upper()
        category = incident.get("type") or incident.get("category", "other")
        title = incident.get("title", "Untitled")
        location = incident.get("location", "Unknown")
        date = incident.get("created_at", "N/A")
        if hasattr(date, "strftime"):
            date = date.strftime("%Y-%m-%d %H:%M")

        return f"[{severity}] {category} - {title} ({location}) - {date}"

    def format_incident_detail(self, incident: dict) -> str:
        """Format an incident as a multi-line detailed view.

        Args:
            incident: Dict with incident fields.

        Returns:
            Multi-line formatted string.
        """
        severity = incident.get("severity", "unknown").upper()
        category = incident.get("type") or incident.get("category", "other")
        title = incident.get("title", "Untitled")
        description = incident.get("description", "No description provided.")
        location = incident.get("location", "Unknown")
        status = incident.get("status", "open")
        date = incident.get("created_at", "N/A")
        incident_id = incident.get("id", "N/A")
        reporter = incident.get("reported_by", "Anonymous")

        if hasattr(date, "strftime"):
            date = date.strftime("%Y-%m-%d %H:%M")

        lines = [
            "=" * 50,
            f"Incident: {title}",
            "=" * 50,
            f"  ID:          {incident_id}",
            f"  Category:    {category}",
            f"  Severity:    {severity}",
            f"  Status:      {status}",
            f"  Location:    {location}",
            f"  Reported by: {reporter}",
            f"  Date:        {date}",
            "-" * 50,
            f"  Description:",
            f"    {description}",
            "=" * 50,
        ]
        return "\n".join(lines)

    def to_csv(self, incidents: list) -> str:
        """Convert a list of incidents to CSV format.

        Columns: id, title, category, severity, status, location,
                 description, created_at

        Args:
            incidents: List of incident dicts.

        Returns:
            CSV string with header row.
        """
        output = io.StringIO()
        fieldnames = [
            "id", "title", "category", "severity", "status",
            "location", "description", "created_at",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()

        for inc in incidents:
            row = {
                "id": inc.get("id", ""),
                "title": inc.get("title", ""),
                "category": inc.get("type") or inc.get("category", ""),
                "severity": inc.get("severity", ""),
                "status": inc.get("status", ""),
                "location": inc.get("location", ""),
                "description": inc.get("description", ""),
                "created_at": inc.get("created_at", ""),
            }
            if hasattr(row["created_at"], "strftime"):
                row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M")
            writer.writerow(row)

        return output.getvalue()

    def format_alert(self, incident: dict) -> str:
        """Format an incident as an alert notification (suitable for SNS).

        Args:
            incident: Dict with incident fields.

        Returns:
            Alert text string.
        """
        severity = incident.get("severity", "unknown").upper()
        category = incident.get("type") or incident.get("category", "other")
        title = incident.get("title", "Untitled")
        location = incident.get("location", "Unknown")
        description = incident.get("description", "")
        date = incident.get("created_at", "N/A")
        if hasattr(date, "strftime"):
            date = date.strftime("%Y-%m-%d %H:%M")

        lines = [
            f"*** SAFETY ALERT [{severity}] ***",
            f"Type: {category}",
            f"Title: {title}",
            f"Location: {location}",
            f"Time: {date}",
            f"Details: {description[:200]}",
            "",
            "Please take appropriate action.",
        ]
        return "\n".join(lines)

    def format_stats_dashboard(self, stats: dict) -> str:
        """Format statistics as a text dashboard.

        Args:
            stats: Dict as returned by SafetyAnalytics.get_incident_stats().

        Returns:
            Formatted dashboard string.
        """
        lines = [
            "+-------------------------------+",
            "|     SAFETY STATS DASHBOARD    |",
            "+-------------------------------+",
            f"  Total Incidents: {stats.get('total', 0)}",
            "",
        ]

        lines.append("  Categories:")
        for cat, count in sorted(
            stats.get("by_category", {}).items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            bar = "#" * count
            lines.append(f"    {cat:<22} {count:>3}  {bar}")

        lines.append("")
        lines.append("  Severity:")
        for sev, count in sorted(
            stats.get("by_severity", {}).items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            bar = "#" * count
            lines.append(f"    {sev:<22} {count:>3}  {bar}")

        lines.append("")
        lines.append("  Status:")
        for status, count in sorted(
            stats.get("by_status", {}).items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            bar = "#" * count
            lines.append(f"    {status:<22} {count:>3}  {bar}")

        lines.append("+-------------------------------+")
        return "\n".join(lines)
