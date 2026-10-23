"""Evaluation router — GET /evaluation/metrics (admin only)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import User
from app.resolution.evaluation import evaluate_resolution
from app.schemas.evaluation import EvaluationMetricsOut

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.get("/metrics", response_model=EvaluationMetricsOut)
def get_metrics(
    _current: User = Depends(require_role("admin")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return evaluate_resolution(db)
