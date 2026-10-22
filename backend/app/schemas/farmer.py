"""Pydantic schemas for the Farmer 360 detail payload."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LinkedRecordOut(BaseModel):
    id: int
    method: str
    score: float | None = None
    source_name: str | None = None


class EnrollmentOut(BaseModel):
    id: int
    scheme_id: int
    scheme_code: str | None = None
    season: str | None = None
    amount: float | None = None


class FlagSummaryOut(BaseModel):
    id: int
    type: str
    severity: str
    reason: str
    status: str


class RecommendationSummaryOut(BaseModel):
    id: int
    scheme_id: int
    scheme_code: str | None = None
    eligible: bool
    already_enrolled: bool
    reasons: list[Any] = []


class FarmerDetailOut(BaseModel):
    id: int
    name: str
    father_name: str | None = None
    dob: str | None = None
    mobile: str | None = None
    village_code: str | None = None
    district_code: str | None = None
    total_land_ha: float | None = None
    category: str | None = None
    confidence: float | None = None
    linked_records: list[LinkedRecordOut] = []
    enrollments: list[EnrollmentOut] = []
    flags: list[FlagSummaryOut] = []
    recommendations: list[RecommendationSummaryOut] = []
