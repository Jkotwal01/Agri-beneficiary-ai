"""Pydantic schemas for farmer listing."""
from __future__ import annotations

from pydantic import BaseModel


class FarmerSummaryOut(BaseModel):
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
    status: str

    model_config = {"from_attributes": True}
