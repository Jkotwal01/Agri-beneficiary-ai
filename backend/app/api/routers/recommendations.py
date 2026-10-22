"""Recommendations router — GET /recommendations."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.recommendation import Recommendation
from app.schemas.recommendations import RecommendationOut

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=list[RecommendationOut])
def list_recommendations(
    farmer_id: int | None = None,
    eligible_only: bool = False,
    db: Session = Depends(get_db),  # noqa: B008
):
    q = db.query(Recommendation)
    if farmer_id is not None:
        q = q.filter(Recommendation.farmer_id == farmer_id)
    if eligible_only:
        q = q.filter(Recommendation.eligible.is_(True))
    return q.order_by(Recommendation.priority.desc()).all()
