"""Pydantic schemas for match review queue."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ShapFeatureOut(BaseModel):
    feature: str
    value: str
    shap_value: float


class CleanRecordOut(BaseModel):
    id: int
    source_name: str | None = None
    name_norm: str | None = None
    mobile10: str | None = None
    district_code: str | None = None
    village_code: str | None = None
    survey_no: str | None = None
    dob: str | None = None

    model_config = {"from_attributes": True}


class MatchCandidateOut(BaseModel):
    id: int
    score: float
    decision: str
    record_a: CleanRecordOut | None = None
    record_b: CleanRecordOut | None = None
    features: dict[str, Any] | None = None
    shap: list[ShapFeatureOut] = []
    reviewed_by: int | None = None
    reviewed_at: datetime | None = None


class MatchDecisionIn(BaseModel):
    decision: str  # confirm | reject
