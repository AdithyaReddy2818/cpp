"""Input validation for incident reports and user data."""

import re


ALLOWED_CATEGORIES = [
    "theft", "vandalism", "suspicious_activity", "accident",
    "noise_complaint", "fire", "flooding", "assault", "other",
]


class ReportValidator:
    """Validates and sanitises incident report and user data."""

    def validate_report(self, data: dict) -> tuple:
        """Validate an incident report payload.

        Checks:
            - title: required, 5-200 characters
            - description: required, 10-2000 characters
            - category: must be in the allowed list
            - location: required, non-empty string

        Args:
            data: Dictionary with report fields.

        Returns:
            Tuple of (is_valid: bool, errors: list[str]).
        """
        errors = []

        # Title
        title = data.get("title", "")
        if not title or not isinstance(title, str):
            errors.append("Title is required.")
        elif len(title.strip()) < 5:
            errors.append("Title must be at least 5 characters.")
        elif len(title.strip()) > 200:
            errors.append("Title must not exceed 200 characters.")

        # Description
        desc = data.get("description", "")
        if not desc or not isinstance(desc, str):
            errors.append("Description is required.")
        elif len(desc.strip()) < 10:
            errors.append("Description must be at least 10 characters.")
        elif len(desc.strip()) > 2000:
            errors.append("Description must not exceed 2000 characters.")

        # Category
        category = data.get("category", "")
        if category and category not in ALLOWED_CATEGORIES:
            errors.append(
                f"Invalid category. Must be one of: {', '.join(ALLOWED_CATEGORIES)}."
            )

        # Location
        location = data.get("location", "")
        if not location or not isinstance(location, str) or not location.strip():
            errors.append("Location is required.")

        return (len(errors) == 0, errors)

    def validate_user(self, data: dict) -> tuple:
        """Validate user registration data.

        Checks:
            - username: 3-30 characters
            - email: must contain '@'
            - password: min 8 chars, at least 1 uppercase letter, 1 digit

        Args:
            data: Dictionary with user fields.

        Returns:
            Tuple of (is_valid: bool, errors: list[str]).
        """
        errors = []

        # Username
        username = data.get("username", "")
        if not username or not isinstance(username, str):
            errors.append("Username is required.")
        elif len(username.strip()) < 3:
            errors.append("Username must be at least 3 characters.")
        elif len(username.strip()) > 30:
            errors.append("Username must not exceed 30 characters.")

        # Email
        email = data.get("email", "")
        if not email or not isinstance(email, str):
            errors.append("Email is required.")
        elif "@" not in email:
            errors.append("Email must contain '@'.")

        # Password
        password = data.get("password", "")
        if not password or not isinstance(password, str):
            errors.append("Password is required.")
        else:
            if len(password) < 8:
                errors.append("Password must be at least 8 characters.")
            if not re.search(r"[A-Z]", password):
                errors.append("Password must contain at least one uppercase letter.")
            if not re.search(r"\d", password):
                errors.append("Password must contain at least one digit.")

        return (len(errors) == 0, errors)

    def sanitize_input(self, text: str) -> str:
        """Strip HTML tags from text.

        Args:
            text: Raw input string.

        Returns:
            Text with all HTML tags removed.
        """
        if not text:
            return ""
        return re.sub(r"<[^>]+>", "", text)

    def validate_coordinates(self, lat: float, lng: float) -> tuple:
        """Validate geographic coordinates.

        Args:
            lat: Latitude (-90 to 90).
            lng: Longitude (-180 to 180).

        Returns:
            Tuple of (is_valid: bool, errors: list[str]).
        """
        errors = []

        try:
            lat = float(lat)
        except (TypeError, ValueError):
            errors.append("Latitude must be a number.")
            return (False, errors)

        try:
            lng = float(lng)
        except (TypeError, ValueError):
            errors.append("Longitude must be a number.")
            return (False, errors)

        if lat < -90 or lat > 90:
            errors.append("Latitude must be between -90 and 90.")
        if lng < -180 or lng > 180:
            errors.append("Longitude must be between -180 and 180.")

        return (len(errors) == 0, errors)
