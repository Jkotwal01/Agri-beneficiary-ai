"""ApplicationService — prefill, submit and decide scheme applications."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.applications.autofill import autofill
from app.applications.form_loader import load_form
from app.applications.validators import validate_submission
from app.models.audit_log import AuditLog
from app.models.enrollment import Enrollment
from app.models.farmer_profile import FarmerProfile
from app.models.scheme import Scheme
from app.models.scheme_application import SchemeApplication

_ACTIVE_APPLICATION_STATUSES = ["submitted", "approved"]


class ApplicationService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def _get_scheme(self, scheme_code: str) -> Scheme:
        scheme = self._db.query(Scheme).filter(Scheme.code == scheme_code).first()
        if not scheme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Scheme not found"
            )
        return scheme

    def prefill(self, profile: FarmerProfile, scheme_code: str) -> dict:
        form_fields = load_form(scheme_code)
        values, autofilled_keys = autofill(form_fields, profile)
        return {"values": values, "autofilled_keys": autofilled_keys}

    def submit(
        self, profile: FarmerProfile, scheme_code: str, form_data: dict
    ) -> SchemeApplication:
        scheme = self._get_scheme(scheme_code)
        form_fields = load_form(scheme_code)

        errors = validate_submission(form_fields, form_data)
        if errors:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)

        existing = (
            self._db.query(SchemeApplication)
            .filter(
                SchemeApplication.farmer_profile_id == profile.id,
                SchemeApplication.scheme_id == scheme.id,
                SchemeApplication.status.in_(_ACTIVE_APPLICATION_STATUSES),
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An active application for this scheme already exists",
            )

        application = SchemeApplication(
            farmer_profile_id=profile.id,
            scheme_id=scheme.id,
            status="submitted",
            form_data=form_data,
            autofilled_keys=[k for k, v in form_data.items() if v is not None],
            submitted_at=datetime.now(UTC),
        )
        self._db.add(application)
        self._db.commit()
        self._db.refresh(application)
        return application

    def decide(
        self, application_id: int, decision: str, reviewer_id: int, note: str | None
    ) -> SchemeApplication:
        if decision not in ("approved", "rejected"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="status must be 'approved' or 'rejected'",
            )

        application = self._db.get(SchemeApplication, application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
            )

        application.status = decision
        application.reviewed_by = reviewer_id
        application.officer_note = note

        if decision == "approved":
            profile = self._db.get(FarmerProfile, application.farmer_profile_id)
            if profile and profile.farmer_id is not None:
                self._db.add(
                    Enrollment(
                        farmer_id=profile.farmer_id, scheme_id=application.scheme_id
                    )
                )

        self._db.add(
            AuditLog(
                user_id=reviewer_id,
                action=f"application_decision→{decision}",
                entity="scheme_applications",
                entity_id=application_id,
            )
        )
        self._db.commit()
        self._db.refresh(application)
        return application
