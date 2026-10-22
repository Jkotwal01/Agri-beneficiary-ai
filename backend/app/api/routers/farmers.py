"""Farmers router — role-gated golden-record listing and detail endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.farmer import Farmer
from app.models.user import User
from app.schemas.farmer import FarmerDetailOut, FarmerSummaryOut
from app.services.farmer_service import FarmerService

router = APIRouter(prefix="/farmers", tags=["farmers"])


@router.get("", response_model=list[FarmerSummaryOut])
def list_farmers(
    q: str | None = None,
    district: str | None = None,
    limit: int = 50,
    offset: int = 0,
    _current: User = Depends(require_role("admin", "officer")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> list[FarmerSummaryOut]:
    """Return golden-record farmers, accessible to admin and officer only."""
    query = db.query(Farmer)
    if q:
        query = query.filter(Farmer.name.ilike(f"%{q}%"))
    if district:
        query = query.filter(Farmer.district_code == district)

    rows = query.order_by(Farmer.id).offset(offset).limit(limit).all()
    return [
        FarmerSummaryOut(
            **{c.name: getattr(row, c.name) for c in Farmer.__table__.columns},
            status="Golden" if (row.confidence or 0) >= 0.9 else "Review",
        )
        for row in rows
    ]


@router.get("/{farmer_id}", response_model=FarmerDetailOut)
def get_farmer_detail(
    farmer_id: int,
    _current: User = Depends(require_role("admin", "officer")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    """Return the full Farmer 360 payload — accessible to admin and officer only."""
    return FarmerService(db).get_detail(farmer_id)
