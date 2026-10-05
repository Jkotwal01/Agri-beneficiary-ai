"""Farmers router — role-gated farmer listing endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import User

router = APIRouter(prefix="/farmers", tags=["farmers"])


@router.get("", status_code=200)
def list_farmers(
    _current: User = Depends(require_role("admin", "officer")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> list[dict]:
    """Return farmers list — accessible to admin and officer only."""
    farmers = db.query(User).filter(User.role == "farmer").all()
    return [{"id": u.id, "email": u.email, "role": u.role} for u in farmers]
