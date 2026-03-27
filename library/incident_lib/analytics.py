"""Safety analytics and reporting."""

import math
from collections import Counter
from datetime import datetime, timedelta, timezone


class SafetyAnalytics:
    """Generates statistics, hotspot analysis, trends, and safety reports."""

    def get_incident_stats(self, incidents: list) -> dict:
        """Compute aggregate statistics for a list of incidents.

        Args:
            incidents: List of incident dicts. Each should have keys like
                       'type'/'category', 'severity', 'status'.

        Returns:
            Dict with keys: total, by_category, by_severity, by_status.
        """
        total = len(incidents)
        by_category = Counter()
        by_severity = Counter()
        by_status = Counter()

        for inc in incidents:
            cat = inc.get("type") or inc.get("category", "other")
            by_category[cat] += 1
            by_severity[inc.get("severity", "unknown")] += 1
            by_status[inc.get("status", "open")] += 1

        return {
            "total": total,
            "by_category": dict(by_category),
            "by_severity": dict(by_severity),
            "by_status": dict(by_status),
        }

    def get_hotspot_areas(self, incidents: list, grid_size: float = 0.01) -> list:
        """Identify hotspot areas by grouping incidents on a lat/lng grid.

        Args:
            incidents: List of incident dicts with 'latitude' and 'longitude'.
            grid_size: Size of the grid cell in degrees (default 0.01).

        Returns:
            List of dicts sorted by count descending. Each dict has keys:
            'lat', 'lng', 'count'.
        """
        grid = Counter()

        for inc in incidents:
            lat = inc.get("latitude")
            lng = inc.get("longitude")
            if lat is None or lng is None:
                continue
            try:
                rounded_lat = round(float(lat) / grid_size) * grid_size
                rounded_lng = round(float(lng) / grid_size) * grid_size
                # Round to avoid floating-point drift
                rounded_lat = round(rounded_lat, 6)
                rounded_lng = round(rounded_lng, 6)
                grid[(rounded_lat, rounded_lng)] += 1
            except (TypeError, ValueError):
                continue

        result = [
            {"lat": k[0], "lng": k[1], "count": v}
            for k, v in grid.items()
        ]
        result.sort(key=lambda x: x["count"], reverse=True)
        return result

    def get_trend_data(self, incidents: list, days: int = 30) -> list:
        """Return daily incident counts for the most recent N days.

        Args:
            incidents: List of incident dicts with 'created_at' (ISO string
                       or datetime).
            days: Number of days to look back (default 30).

        Returns:
            List of dicts with 'date' (YYYY-MM-DD) and 'count', one per day,
            ordered chronologically.
        """
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=days)

        daily = Counter()
        for inc in incidents:
            created = inc.get("created_at")
            if not created:
                continue
            if isinstance(created, str):
                try:
                    created = datetime.fromisoformat(created.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    continue
            if isinstance(created, datetime):
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                if created >= start:
                    day_str = created.strftime("%Y-%m-%d")
                    daily[day_str] += 1

        result = []
        for i in range(days):
            d = start + timedelta(days=i + 1)
            day_str = d.strftime("%Y-%m-%d")
            result.append({"date": day_str, "count": daily.get(day_str, 0)})

        return result

    def generate_safety_report(self, incidents: list, area_name: str = "Neighbourhood") -> str:
        """Generate a formatted text safety report.

        Args:
            incidents: List of incident dicts.
            area_name: Name of the area for the report header.

        Returns:
            Multi-line formatted report string.
        """
        stats = self.get_incident_stats(incidents)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        lines = [
            f"=== Safety Report: {area_name} ===",
            f"Generated: {now}",
            "",
            f"Total Incidents: {stats['total']}",
            "",
            "--- By Category ---",
        ]
        for cat, count in sorted(stats["by_category"].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {cat}: {count}")

        lines.append("")
        lines.append("--- By Severity ---")
        for sev, count in sorted(stats["by_severity"].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {sev}: {count}")

        lines.append("")
        lines.append("--- By Status ---")
        for status, count in sorted(stats["by_status"].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {status}: {count}")

        # Recommendations
        lines.append("")
        lines.append("--- Recommendations ---")
        if stats["by_category"].get("assault", 0) > 0 or stats["by_category"].get("fire", 0) > 0:
            lines.append("  - URGENT: Critical incidents detected. Increase patrols and emergency readiness.")
        if stats["by_category"].get("theft", 0) >= 3:
            lines.append("  - High theft activity. Consider neighbourhood watch programmes.")
        if stats["by_category"].get("vandalism", 0) >= 2:
            lines.append("  - Vandalism reports noted. Improve lighting and CCTV coverage.")
        if stats["total"] == 0:
            lines.append("  - No incidents reported. Continue community engagement.")
        elif stats["total"] <= 5:
            lines.append("  - Low incident volume. Maintain current safety measures.")

        return "\n".join(lines)

    def get_recent_incidents(self, incidents: list, hours: int = 24) -> list:
        """Filter incidents from the last N hours.

        Args:
            incidents: List of incident dicts with 'created_at'.
            hours: Look-back window in hours (default 24).

        Returns:
            Filtered list of incidents.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        result = []

        for inc in incidents:
            created = inc.get("created_at")
            if not created:
                continue
            if isinstance(created, str):
                try:
                    created = datetime.fromisoformat(created.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    continue
            if isinstance(created, datetime):
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                if created >= cutoff:
                    result.append(inc)

        return result
