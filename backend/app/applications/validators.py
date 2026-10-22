"""Validators — checks submitted application form_data against required fields."""

from __future__ import annotations


def validate_submission(form_fields: list[dict], form_data: dict) -> list[str]:
    """Return a list of error strings for required fields missing from form_data."""
    errors: list[str] = []
    for field in form_fields:
        if not field.get("required"):
            continue
        value = form_data.get(field["key"])
        if value in (None, "", []):
            errors.append(f"{field['label']} is required")
    return errors
