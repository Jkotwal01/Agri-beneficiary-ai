"""Pydantic schemas for recommendations."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class RecommendationOut(BaseModel):
    id: int
    farmer_id: int
    scheme_id: int
    eligible: bool
    reasons_json: list[Any] | None = None
    already_enrolled: bool
    priority: int

    model_config = {"from_attributes": True}
