"""Me router — farmer's own profile and recommended-scheme feed."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.farmer_profile import FarmerProfile
from app.models.user import User
from app.schemas.profile import ProfileIn, ProfileOut, RecommendedSchemeOut
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/me", tags=["me"])


def _get_or_create_profile(db: Session, user_id: int) -> FarmerProfile:
    """Return the farmer's profile, auto-creating an empty shell if not yet present.

    This prevents newly-registered farmers from seeing a hard 404 on their
    first visit to /me — instead the UI receives an empty profile with
    completeness=0 and can show the "Build your profile" prompt.
    """
    profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == user_id).first()
    if profile is None:
        profile = FarmerProfile(user_id=user_id, completeness=0, verified=False)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.get("/profile", response_model=ProfileOut)
def get_profile(
    current: User = Depends(require_role("farmer")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return _get_or_create_profile(db, current.id)


@router.put("/profile", response_model=ProfileOut)
def put_profile(
    payload: ProfileIn,
    current: User = Depends(require_role("farmer")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    return ProfileService(db).save_profile(
        current.id, payload.model_dump(exclude_unset=True)
    )


@router.get("/schemes", response_model=list[RecommendedSchemeOut])
def get_recommended_schemes(
    section: str = "recommended",
    current: User = Depends(require_role("farmer")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    profile = _get_or_create_profile(db, current.id)
    if section != "recommended":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported section"
        )
    return ProfileService(db).recommended_schemes(profile)
