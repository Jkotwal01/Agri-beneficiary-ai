"""Pydantic schemas for reports and exclusions."""
from __future__ import annotations

from pydantic import BaseModel


class SummaryOut(BaseModel):
    total_records: int
    unique_farmers: int
    open_flags: int
    exclusions: int


class SchemeCoverage(BaseModel):
    scheme_code: str
    enrolled_count: int


class CoverageOut(BaseModel):
    group: str
    count: int
    scheme_coverage: list[SchemeCoverage]


class ExclusionOut(BaseModel):
    farmer_id: int
    farmer_name: str
    district_code: str | None = None
    village_code: str | None = None
    scheme_code: str
    reasons: list[str] = []

    model_config = {"from_attributes": True}
