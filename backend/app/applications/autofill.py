"""
Autofill — Spec Section 16, 1-click autofill for scheme applications.

autofill(form_fields, profile) -> (values, autofilled_keys)
  Each form field may declare `autofill_from: <profile attribute name>`.
  If that attribute is non-empty on the profile, its value fills the field
  and the field's key is added to autofilled_keys. Fields without a usable
  autofill_from source are left blank for the farmer to fill manually.
"""

from __future__ import annotations

from typing import Any


def autofill(form_fields: list[dict], profile: Any) -> tuple[dict, list[str]]:
    values: dict = {}
    autofilled_keys: list[str] = []

    for field in form_fields:
        key = field["key"]
        source = field.get("autofill_from")
        value = getattr(profile, source, None) if source else None

        if value not in (None, "", []):
            values[key] = value
            autofilled_keys.append(key)
        else:
            values[key] = None

    return values, autofilled_keys
