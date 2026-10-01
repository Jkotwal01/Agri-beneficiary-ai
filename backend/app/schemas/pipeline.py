"""Pydantic schemas for pipeline endpoints."""

from __future__ import annotations

from pydantic import BaseModel


class PipelineResponse(BaseModel):
    status: str
    details: dict[str, int] = {}
