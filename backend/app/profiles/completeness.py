"""
Profile completeness — Spec Section 16, Farmer Portal.

score(profile) -> int in [0, 100], the percentage of the "important" profile
fields that are filled in. Used to drive the ProfileWizard's progress meter.
"""

from __future__ import annotations

from app.models.farmer_profile import FarmerProfile

IMPORTANT_FIELDS = [
    "full_name",
    "father_name",
    "dob",
    "gender",
    "mobile",
    "village",
    "taluka",
    "district",
    "state",
    "pincode",
    "total_land_ha",
    "ownership_type",
    "main_crops",
    "irrigation_type",
]


def score(profile: FarmerProfile) -> int:
    """Return the percentage of IMPORTANT_FIELDS that are non-empty on `profile`."""
    filled = 0
    for field in IMPORTANT_FIELDS:
        value = getattr(profile, field, None)
        if value not in (None, "", []):
            filled += 1
    return round((filled / len(IMPORTANT_FIELDS)) * 100)
