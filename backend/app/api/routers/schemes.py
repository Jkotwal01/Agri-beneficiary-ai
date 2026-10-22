"""Schemes router — list schemes, admin publish (triggers scheme alert emails)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_role
from app.models.scheme import Scheme
from app.models.user import User
from app.notifications.sender import get_email_sender
from app.schemas.scheme import SchemeOut
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/schemes", tags=["schemes"])


@router.get("", response_model=list[SchemeOut])
def list_schemes(
    _current: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return db.query(Scheme).order_by(Scheme.code).all()


@router.post("/{scheme_code}/publish", response_model=SchemeOut)
def publish_scheme(
    scheme_code: str,
    _current: User = Depends(require_role("admin")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    """Mark a scheme active and alert opted-in farmers whose interests match its domain."""
    scheme = db.query(Scheme).filter(Scheme.code == scheme_code).first()
    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Scheme not found"
        )

    scheme.status = "active"
    db.commit()
    db.refresh(scheme)

    NotificationService(db, get_email_sender()).send_scheme_alert(scheme)
    return scheme
