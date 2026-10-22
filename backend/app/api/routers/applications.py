"""Applications router — farmer prefill/submit, officer inbox/decision."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.farmer_profile import FarmerProfile
from app.models.scheme_application import SchemeApplication
from app.models.user import User
from app.schemas.application import (
    ApplicationDecisionIn,
    ApplicationOut,
    ApplicationSubmit,
    PrefillRequest,
    PrefillResponse,
)
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["applications"])


def _own_profile(db: Session, user_id: int) -> FarmerProfile:
    profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == user_id).first()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )
    return profile


@router.post("/prefill", response_model=PrefillResponse)
def prefill(
    body: PrefillRequest,
    current: User = Depends(require_role("farmer")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    profile = _own_profile(db, current.id)
    return ApplicationService(db).prefill(profile, body.scheme_code)


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def submit(
    body: ApplicationSubmit,
    current: User = Depends(require_role("farmer")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    profile = _own_profile(db, current.id)
    return ApplicationService(db).submit(profile, body.scheme_code, body.form_data)


@router.get("", response_model=list[ApplicationOut])
def list_applications(
    status_filter: str | None = None,
    current: User = Depends(require_role("admin", "officer", "farmer")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    """Officers/admins see every application; a farmer sees only their own."""
    q = db.query(SchemeApplication)
    if current.role == "farmer":
        profile = _own_profile(db, current.id)
        q = q.filter(SchemeApplication.farmer_profile_id == profile.id)
    if status_filter:
        q = q.filter(SchemeApplication.status == status_filter)
    return q.order_by(SchemeApplication.id).all()


@router.get("/{application_id}", response_model=ApplicationOut)
def get_application(
    application_id: int,
    current: User = Depends(require_role("admin", "officer", "farmer")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    application = db.get(SchemeApplication, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    if current.role == "farmer":
        profile = _own_profile(db, current.id)
        if application.farmer_profile_id != profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not your application"
            )

    return application


@router.patch("/{application_id}/decision", response_model=ApplicationOut)
def decide(
    application_id: int,
    body: ApplicationDecisionIn,
    current: User = Depends(require_role("admin", "officer")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return ApplicationService(db).decide(
        application_id, body.status, current.id, body.note
    )
