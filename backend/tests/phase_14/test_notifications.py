"""
Phase 14 tests — Email Notifications & Profile Linking.

Tests:
  1. ConsoleEmailSender.send() captures output without raising.
  2. send_weekly_digest() with 2 opted-in farmers -> email_log has 2 rows;
     same call again -> 0 new rows (deduplication).
  3. profile_linker with matching mobile -> method=rule, linked.
  4. Profile linker score >= 0.90 -> linked to golden farmer.
  5. Profile linker score < 0.60 -> no link (farmer_id stays None).
  6. PATCH /applications/{id}/decision {approved} -> status email logged.
"""

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import Base, engine
from app.core.security import hash_password
from app.models.email_log import EmailLog
from app.models.farmer import Farmer
from app.models.farmer_profile import FarmerProfile
from app.models.scheme import Scheme
from app.models.scheme_application import SchemeApplication
from app.models.user import User
from app.notifications.sender import ConsoleEmailSender
from app.profiles.profile_linker import link
from app.services.application_service import ApplicationService
from app.services.notification_service import NotificationService

TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_TABLES = (
    "email_log",
    "audit_log",
    "scheme_applications",
    "enrollments",
    "farmer_profiles",
    "recommendations",
    "farmers",
    "schemes",
)


def _get_or_create_user(db: Session, email: str, role: str = "farmer") -> User:
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        user = User(email=email, password_hash=hash_password("Secret123!"), role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@pytest.fixture(scope="module")
def seeded_db():
    Base.metadata.create_all(bind=engine)
    db: Session = TestingSession()
    for table in _TABLES:
        db.execute(text(f"DELETE FROM {table}"))
    db.commit()

    yield db

    for table in _TABLES:
        db.execute(text(f"DELETE FROM {table}"))
    db.commit()
    db.close()


# ===========================================================================
# 1. ConsoleEmailSender
# ===========================================================================
def test_console_email_sender_prints_without_raising(capsys):
    sender = ConsoleEmailSender()
    sender.send("farmer@example.com", "Test Subject", "<p>Hello</p>")
    captured = capsys.readouterr()
    assert "farmer@example.com" in captured.out
    assert "Test Subject" in captured.out


# ===========================================================================
# 2. send_weekly_digest + dedup
# ===========================================================================
def test_weekly_digest_dedup(seeded_db):
    db = seeded_db
    for table in _TABLES:
        db.execute(text(f"DELETE FROM {table}"))
    db.commit()

    db.add(
        Scheme(code="PM_KISAN", name="PM_KISAN", domain="AGRICULTURE", benefit_score=10)
    )
    db.commit()

    user_one = _get_or_create_user(db, "phase14_farmer_one@example.com")
    user_two = _get_or_create_user(db, "phase14_farmer_two@example.com")

    db.add_all(
        [
            FarmerProfile(
                user_id=user_one.id,
                full_name="Farmer One",
                mobile="9000000001",
                total_land_ha=1.0,
                interests=["AGRICULTURE"],
                email="one@example.com",
                email_opt_in=True,
            ),
            FarmerProfile(
                user_id=user_two.id,
                full_name="Farmer Two",
                mobile="9000000002",
                total_land_ha=1.5,
                interests=["AGRICULTURE"],
                email="two@example.com",
                email_opt_in=True,
            ),
        ]
    )
    db.commit()

    sender = ConsoleEmailSender()
    service = NotificationService(db, sender)

    sent_first = service.send_weekly_digest()
    assert sent_first == 2
    assert db.query(EmailLog).filter(EmailLog.type == "digest").count() == 2

    sent_second = service.send_weekly_digest()
    assert sent_second == 0
    assert db.query(EmailLog).filter(EmailLog.type == "digest").count() == 2


# ===========================================================================
# 3. profile_linker — mobile match -> method=rule
# ===========================================================================
def test_profile_linker_rule_match_on_mobile(seeded_db):
    db = seeded_db
    farmer = Farmer(name="Ramesh Kotwal", mobile="9876543210", confidence=0.95)
    db.add(farmer)
    db.commit()

    user = _get_or_create_user(db, "phase14_rule_match@example.com")
    profile = FarmerProfile(user_id=user.id, full_name="R. Kotwal", mobile="9876543210")
    farmer_id, method, score = link(db, profile)

    assert farmer_id == farmer.id
    assert method == "rule"
    assert score == 1.0


# ===========================================================================
# 4. profile_linker — high name similarity -> method=score, linked
# ===========================================================================
def test_profile_linker_score_match_links(seeded_db):
    db = seeded_db
    farmer = Farmer(name="Suresh Patil", mobile=None, confidence=0.9)
    db.add(farmer)
    db.commit()

    user = _get_or_create_user(db, "phase14_score_match@example.com")
    profile = FarmerProfile(
        user_id=user.id, full_name="Suresh Patil", mobile="9111111111"
    )
    farmer_id, method, score = link(db, profile)

    assert farmer_id == farmer.id
    assert method == "score"
    assert score >= 0.90


# ===========================================================================
# 5. profile_linker — low similarity -> no link
# ===========================================================================
def test_profile_linker_low_score_no_link(seeded_db):
    db = seeded_db
    user = _get_or_create_user(db, "phase14_no_match@example.com")
    profile = FarmerProfile(
        user_id=user.id, full_name="Zzyx Qvlpt", mobile="9222222222"
    )
    farmer_id, method, score = link(db, profile)

    assert farmer_id is None
    assert method == "none"
    assert score < 0.60


# ===========================================================================
# 6. Application decision -> status email logged
# ===========================================================================
def test_application_decision_logs_status_email(seeded_db):
    db = seeded_db
    scheme = db.query(Scheme).filter(Scheme.code == "PM_KISAN").first()
    if scheme is None:
        scheme = Scheme(code="PM_KISAN", name="PM_KISAN", benefit_score=10)
        db.add(scheme)
        db.commit()

    farmer_user = _get_or_create_user(db, "phase14_status_farmer@example.com")
    officer_user = _get_or_create_user(
        db, "phase14_status_officer@example.com", role="officer"
    )

    profile = FarmerProfile(
        user_id=farmer_user.id,
        full_name="Status Test Farmer",
        mobile="9333333333",
        email="status@example.com",
    )
    db.add(profile)
    db.commit()

    application = SchemeApplication(
        farmer_profile_id=profile.id,
        scheme_id=scheme.id,
        status="submitted",
        form_data={},
        autofilled_keys=[],
    )
    db.add(application)
    db.commit()

    service = ApplicationService(db, sender=ConsoleEmailSender())
    service.decide(
        application.id, "approved", reviewer_id=officer_user.id, note="Looks good"
    )

    email = (
        db.query(EmailLog)
        .filter(EmailLog.farmer_profile_id == profile.id, EmailLog.type == "status")
        .first()
    )
    assert email is not None
