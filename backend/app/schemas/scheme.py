"""Pydantic schemas for scheme listing."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class SchemeOut(BaseModel):
    id: int
    code: str
    name: str
    description: str | None = None
    domain: str | None = None
    status: str | None = None
    start_date: date | None = None
    end_date: date | None = None

    model_config = {"from_attributes": True}
