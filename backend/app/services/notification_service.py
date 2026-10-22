"""NotificationService — weekly digest, scheme alerts, and application status emails."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.email_log import EmailLog
from app.models.farmer_profile import FarmerProfile
from app.models.scheme import Scheme
from app.models.scheme_application import SchemeApplication
from app.notifications.digest_builder import render_alert, render_digest, render_status
from app.notifications.sender import EmailSender
from app.services.profile_service import ProfileService


class NotificationService:
    def __init__(self, db: Session, sender: EmailSender) -> None:
        self._db = db
        self._sender = sender

    def _already_sent(
        self, farmer_profile_id: int, type_: str, scheme_id: int | None = None
    ) -> bool:
        q = self._db.query(EmailLog).filter(
            EmailLog.farmer_profile_id == farmer_profile_id, EmailLog.type == type_
        )
        if scheme_id is not None:
            q = q.filter(EmailLog.scheme_id == scheme_id)
        return q.first() is not None

    def send_weekly_digest(self) -> int:
        """Send the weekly scheme-match digest to every opted-in farmer. Returns count sent."""
        profile_service = ProfileService(self._db)
        sent = 0

        profiles = (
            self._db.query(FarmerProfile)
            .filter(
                FarmerProfile.email_opt_in.is_(True), FarmerProfile.email.isnot(None)
            )
            .all()
        )
        for profile in profiles:
            if self._already_sent(profile.id, "digest"):
                continue

            schemes = profile_service.recommended_schemes(profile)
            if not schemes:
                continue

            subject, body = render_digest(profile.full_name or "Farmer", schemes)
            self._sender.send(profile.email, subject, body)
            self._db.add(EmailLog(farmer_profile_id=profile.id, type="digest"))
            sent += 1

        self._db.commit()
        return sent

    def send_scheme_alert(self, scheme: Scheme) -> int:
        """Alert opted-in farmers whose interests match this scheme's domain. Returns count sent."""
        sent = 0
        profiles = (
            self._db.query(FarmerProfile)
            .filter(
                FarmerProfile.email_opt_in.is_(True), FarmerProfile.email.isnot(None)
            )
            .all()
        )
        for profile in profiles:
            interests = profile.interests or []
            if scheme.domain and scheme.domain not in interests:
                continue
            if self._already_sent(profile.id, "alert", scheme.id):
                continue

            subject, body = render_alert(
                profile.full_name or "Farmer", scheme.name, scheme.code
            )
            self._sender.send(profile.email, subject, body)
            self._db.add(
                EmailLog(
                    farmer_profile_id=profile.id, type="alert", scheme_id=scheme.id
                )
            )
            sent += 1

        self._db.commit()
        return sent

    def send_status_email(self, application: SchemeApplication) -> None:
        profile = self._db.get(FarmerProfile, application.farmer_profile_id)
        if not profile or not profile.email:
            return

        scheme = self._db.get(Scheme, application.scheme_id)
        scheme_name = scheme.name if scheme else f"Scheme #{application.scheme_id}"

        subject, body = render_status(
            profile.full_name or "Farmer",
            scheme_name,
            application.status,
            application.officer_note,
        )
        self._sender.send(profile.email, subject, body)
        self._db.add(
            EmailLog(
                farmer_profile_id=profile.id,
                type="status",
                scheme_id=application.scheme_id,
            )
        )
        self._db.commit()
