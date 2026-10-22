"""Schemes router — list schemes available to any authenticated user."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.scheme import Scheme
from app.models.user import User
from app.schemas.scheme import SchemeOut

router = APIRouter(prefix="/schemes", tags=["schemes"])


@router.get("", response_model=list[SchemeOut])
def list_schemes(
    _current: User = Depends(get_current_user),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return db.query(Scheme).order_by(Scheme.code).all()
