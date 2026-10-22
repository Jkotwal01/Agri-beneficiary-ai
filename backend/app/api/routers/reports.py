"""Reports router — GET /reports/summary, /reports/coverage, /reports/export."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import User
from app.schemas.reports import CoverageOut, SummaryOut
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary", response_model=SummaryOut)
def get_summary(
    _current: User = Depends(require_role("admin", "officer")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return ReportService(db).summary()


@router.get("/coverage", response_model=list[CoverageOut])
def get_coverage(
    group_by: str = "district",
    _current: User = Depends(require_role("admin", "officer")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return ReportService(db).coverage(group_by=group_by)


@router.get("/export")
def export_report(
    type: str,
    _current: User = Depends(require_role("admin", "officer")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    csv_content = ReportService(db).export_csv(type)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={type}.csv"},
    )
