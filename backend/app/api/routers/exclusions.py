"""Exclusions router — GET /exclusions?district=&scheme=."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import User
from app.schemas.reports import ExclusionOut
from app.services.report_service import ReportService

router = APIRouter(prefix="/exclusions", tags=["exclusions"])


@router.get("", response_model=list[ExclusionOut])
def list_exclusions(
    district: str | None = None,
    scheme: str | None = None,
    _current: User = Depends(require_role("admin", "officer")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return ReportService(db).exclusions(district=district, scheme=scheme)
