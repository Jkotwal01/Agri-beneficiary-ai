"""Pydantic schema for resolution evaluation metrics."""

from __future__ import annotations

from pydantic import BaseModel


class EvaluationMetricsOut(BaseModel):
    precision: float
    recall: float
    f1: float
    auto_link_rate: float
    review_rate: float
