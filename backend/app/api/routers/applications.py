"""Applications router — farmer prefill/submit, officer inbox/decision."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.farmer import Farmer
from app.models.farmer_profile import FarmerProfile
from app.models.flag import Flag
from app.models.scheme import Scheme
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


def _enrich_application(db: Session, app: SchemeApplication) -> ApplicationOut:
    out = ApplicationOut.model_validate(app, from_attributes=True)

    # Scheme details
    scheme = db.get(Scheme, app.scheme_id)
    if scheme:
        out.scheme_name = scheme.name
        out.scheme_code = scheme.code

    # Profile & Farmer details
    profile = db.get(FarmerProfile, app.farmer_profile_id)
    if profile:
        out.applicant_name = profile.full_name
        out.father_name = profile.father_name
        out.farmer_id = profile.farmer_id
        out.mobile = profile.mobile
        out.email = profile.email
        out.village = profile.village
        out.taluka = profile.taluka
        out.district = profile.district
        out.state = profile.state
        out.category = profile.category
        out.total_land_ha = profile.total_land_ha
        out.ownership_type = profile.ownership_type
        out.main_crops = profile.main_crops
        out.bank_name = profile.bank_name
        out.ifsc = profile.ifsc
        out.agristack_id = profile.agristack_id

        # Also fallback to underlying Farmer record if profile fields are sparse
        if profile.farmer_id:
            farmer = db.get(Farmer, profile.farmer_id)
            if farmer:
                if not out.applicant_name:
                    out.applicant_name = farmer.name
                if not out.father_name:
                    out.father_name = farmer.father_name
                if not out.mobile:
                    out.mobile = farmer.mobile
                if not out.total_land_ha and farmer.total_land_ha is not None:
                    out.total_land_ha = farmer.total_land_ha
                if not out.district:
                    out.district = farmer.district_code

            # Load flags for this farmer
            flags = (
                db.query(Flag)
                .filter(Flag.farmer_id == profile.farmer_id)
                .order_by(Flag.id)
                .all()
            )
            out.flags_count = len(flags)
            out.flags = [
                {
                    "id": f.id,
                    "type": f.type,
                    "severity": f.severity,
                    "reason": f.reason,
                    "status": f.status,
                }
                for f in flags
            ]

    # If form_data has full_name or mobile, use it as fallback
    if (
        not out.applicant_name
        and app.form_data
        and isinstance(app.form_data, dict)
        and "full_name" in app.form_data
    ):
        out.applicant_name = str(app.form_data["full_name"])
    if (
        not out.mobile
        and app.form_data
        and isinstance(app.form_data, dict)
        and "mobile" in app.form_data
    ):
        out.mobile = str(app.form_data["mobile"])

    return out


@router.get("", response_model=list[ApplicationOut])
def list_applications(
    status_filter: str | None = None,
    farmer_id: int | None = None,
    search: str | None = None,
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
    if farmer_id is not None:
        profile_ids = [
            p.id
            for p in db.query(FarmerProfile.id)
            .filter(FarmerProfile.farmer_id == farmer_id)
            .all()
        ]
        q = q.filter(SchemeApplication.farmer_profile_id.in_(profile_ids))

    apps = (
        q.order_by(
            SchemeApplication.submitted_at.desc().nullslast(),
            SchemeApplication.id.desc(),
        ).all()
    )
    enriched = [_enrich_application(db, app) for app in apps]

    if search:
        s = search.lower().strip()
        enriched = [
            a
            for a in enriched
            if (a.applicant_name and s in a.applicant_name.lower())
            or (a.mobile and s in a.mobile)
            or (a.scheme_name and s in a.scheme_name.lower())
            or (str(a.id) == s)
            or (a.farmer_id and str(a.farmer_id) == s)
        ]

    return enriched


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

    return _enrich_application(db, application)


@router.patch("/{application_id}/decision", response_model=ApplicationOut)
def decide(
    application_id: int,
    body: ApplicationDecisionIn,
    current: User = Depends(require_role("admin", "officer")),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    decided_app = ApplicationService(db).decide(
        application_id, body.status, current.id, body.note
    )
    return _enrich_application(db, decided_app)
