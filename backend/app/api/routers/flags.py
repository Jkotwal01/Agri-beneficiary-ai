"""Flags router — GET /flags, PATCH /flags/{id}."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.audit_log import AuditLog
from app.models.farmer import Farmer
from app.models.flag import Flag
from app.models.user import User
from app.schemas.flags import FlagOut, FlagPatch

router = APIRouter(prefix="/flags", tags=["flags"])


@router.get("", response_model=list[FlagOut])
def list_flags(
    type: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),  # noqa: B008
):
    q = db.query(Flag, Farmer.name).outerjoin(Farmer, Farmer.id == Flag.farmer_id)
    if type:
        q = q.filter(Flag.type == type)
    if status:
        q = q.filter(Flag.status == status)
    rows = q.order_by(Flag.created_at.desc()).all()
    return [
        FlagOut.model_validate(flag, from_attributes=True).model_copy(
            update={"farmer_name": farmer_name}
        )
        for flag, farmer_name in rows
    ]


@router.patch("/{flag_id}", response_model=FlagOut)
def update_flag(
    flag_id: int,
    body: FlagPatch,
    db: Session = Depends(get_db),  # noqa: B008
):
    flag = db.get(Flag, flag_id)
    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")
    user = db.query(User).first()
    if not user:
        user = User(email="system@agri.gov.in", password_hash="system", role="admin")
        db.add(user)
        db.flush()

    flag.status = body.status
    db.add(
        AuditLog(
            user_id=user.id,
            action=f"flag_status→{body.status}",
            entity="flags",
            entity_id=flag_id,
        )
    )
    db.commit()
    db.refresh(flag)
    return flag
