"""Matches router — GET /matches, POST /matches/{id}/decision."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import User
from app.schemas.matches import MatchCandidateOut, MatchDecisionIn
from app.services.match_service import MatchService

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=list[MatchCandidateOut])
def list_matches(
    decision: str | None = None,
    _current: User = Depends(require_role("admin", "officer")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return MatchService(db).list_matches(decision=decision)


@router.post("/{match_id}/decision", response_model=MatchCandidateOut)
def decide_match(
    match_id: int,
    body: MatchDecisionIn,
    current: User = Depends(require_role("admin", "officer")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return MatchService(db).decide(match_id, body.decision, current.id)
