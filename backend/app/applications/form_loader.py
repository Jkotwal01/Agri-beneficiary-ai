"""Form Loader — reads a scheme's application_form field list from schemes.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml

SCHEMES_YAML = Path(__file__).parent.parent / "eligibility" / "rules" / "schemes.yaml"


def load_form(scheme_code: str) -> list[dict]:
    """Return the application_form field definitions for `scheme_code`, or []."""
    with open(SCHEMES_YAML, encoding="utf-8") as f:
        schemes = yaml.safe_load(f)
    cfg = schemes.get(scheme_code)
    if not cfg:
        return []
    return cfg.get("application_form", [])
