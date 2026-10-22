"""Pydantic schemas for flags."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class FlagOut(BaseModel):
    id: int
    farmer_id: int
    type: str
    severity: str
    reason: str
    status: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class FlagPatch(BaseModel):
    status: str   # open | confirmed | dismissed
