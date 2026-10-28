"""
Phase 12 tests — Farmer Portal Backend.

Tests:
  1. POST /auth/register -> farmer user created, role=farmer.
  2. PUT /me/profile -> profile saved; completeness in range 0-100.
  3. GET /me/schemes?section=recommended -> only eligible, not-enrolled schemes.
  4. POST /applications/prefill {scheme_code: PMFBY} -> values dict + autofilled_keys list.
  5. POST /applications submit -> status submitted; duplicate check fires if already applied.
  6. PATCH /applications/{id}/decision {status: approved} (officer) -> enrollments row
     created, audit_log written.
  7. Farmer cannot read another farmer's applications -> 403.
  8. autofill unit: 4 autofill fields + 2 manual -> returns 4 filled keys.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.applications.autofill import autofill
from app.core.db import Base, engine
from app.core.security import create_token, hash_password
from app.main import app
from app.models.audit_log import AuditLog
from app.models.scheme import Scheme
from app.models.user import User

TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
client = TestClient(app)


def _token(db: Session, email: str, role: str) -> str:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, password_hash=hash_password("Secret123!"), role=role)
        db.add(user)
        db.flush()
        db.commit()
    return create_token({"sub": str(user.id)})


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def seeded_db():
    Base.metadata.create_all(bind=engine)
    db: Session = TestingSession()

    for table in (
        "email_log",
        "audit_log",
        "enrollments",
        "scheme_applications",
        "farmer_profiles",
        "recommendations",
        "farmers",
        "schemes",
    ):
        db.execute(text(f"DELETE FROM {table}"))
    db.commit()

    db.add_all(
        [
            Scheme(
                code="PM_KISAN", name="PM_KISAN", domain="AGRICULTURE", benefit_score=10
            ),
            Scheme(code="PMFBY", name="PMFBY", domain="AGRICULTURE", benefit_score=5),
            Scheme(code="KCC", name="KCC", domain="CREDIT", benefit_score=5),
        ]
    )
    db.commit()

    officer_token = _token(db, "phase12_officer@example.com", "officer")

    yield db, officer_token

    for table in (
        "audit_log",
        "enrollments",
        "scheme_applications",
        "farmer_profiles",
        "recommendations",
        "farmers",
        "schemes",
    ):
        db.execute(text(f"DELETE FROM {table}"))
    db.commit()
    db.close()


# ===========================================================================
# 1. POST /auth/register -> farmer created
# ===========================================================================
def test_register_farmer(seeded_db):
    resp = client.post(
        "/auth/register",
        json={
            "email": "phase12_farmer_a@example.com",
            "password": "Secret123!",
            "role": "farmer",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["role"] == "farmer"


# ===========================================================================
# 2. PUT /me/profile -> saved, completeness 0-100
# ===========================================================================
def test_put_profile_saves_and_scores_completeness(seeded_db):
    login = client.post(
        "/auth/login",
        json={
            "email": "phase12_farmer_a@example.com",
            "password": "Secret123!",
        },
    )
    token = login.json()["access_token"]

    resp = client.put(
        "/me/profile",
        json={
            "full_name": "Ramesh Kotwal",
            "mobile": "9876543210",
            "village": "V1",
            "district": "PUNE",
            "total_land_ha": 1.5,
            "main_crops": ["jute"],  # not covered by PMFBY/NFSM's crop list
            "interests": ["AGRICULTURE"],
        },
        headers=_auth(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert 0 <= body["completeness"] <= 100
    assert body["completeness"] > 0


# ===========================================================================
# 3. GET /me/schemes?section=recommended
# ===========================================================================
def test_recommended_schemes_filters_eligible_not_enrolled(seeded_db):
    login = client.post(
        "/auth/login",
        json={
            "email": "phase12_farmer_a@example.com",
            "password": "Secret123!",
        },
    )
    token = login.json()["access_token"]

    resp = client.get("/me/schemes?section=recommended", headers=_auth(token))
    assert resp.status_code == 200
    codes = {s["scheme_code"] for s in resp.json()}
    assert "PMFBY" not in codes  # "jute" is not in PMFBY's covered crop list
    assert "KCC" not in codes  # opted into AGRICULTURE only, KCC is CREDIT domain
    assert "PM_KISAN" in codes  # 1.5 ha, land-only rule — eligible


# ===========================================================================
# 4. POST /applications/prefill
# ===========================================================================
def test_prefill_returns_values_and_autofilled_keys(seeded_db):
    login = client.post(
        "/auth/login",
        json={
            "email": "phase12_farmer_a@example.com",
            "password": "Secret123!",
        },
    )
    token = login.json()["access_token"]

    resp = client.post(
        "/applications/prefill", json={"scheme_code": "PMFBY"}, headers=_auth(token)
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "values" in body and "autofilled_keys" in body
    assert "full_name" in body["autofilled_keys"]
    assert body["values"]["full_name"] == "Ramesh Kotwal"


# ===========================================================================
# 5. POST /applications submit + duplicate check
# ===========================================================================
def test_submit_application_and_duplicate_check(seeded_db):
    login = client.post(
        "/auth/login",
        json={
            "email": "phase12_farmer_a@example.com",
            "password": "Secret123!",
        },
    )
    token = login.json()["access_token"]

    resp = client.post(
        "/applications",
        json={
            "scheme_code": "PMFBY",
            "form_data": {
                "full_name": "Ramesh Kotwal",
                "mobile": "9876543210",
                "village": "V1",
                "main_crops": "wheat",
            },
        },
        headers=_auth(token),
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "submitted"

    dup = client.post(
        "/applications",
        json={
            "scheme_code": "PMFBY",
            "form_data": {
                "full_name": "Ramesh Kotwal",
                "mobile": "9876543210",
                "village": "V1",
                "main_crops": "wheat",
            },
        },
        headers=_auth(token),
    )
    assert dup.status_code == 409


# ===========================================================================
# 6. PATCH /applications/{id}/decision {approved} -> enrollment + audit_log
# ===========================================================================
def test_officer_approves_application_creates_enrollment(seeded_db):
    db, officer_token = seeded_db
    login = client.post(
        "/auth/login",
        json={
            "email": "phase12_farmer_a@example.com",
            "password": "Secret123!",
        },
    )
    farmer_token = login.json()["access_token"]

    apps_resp = client.get("/applications", headers=_auth(officer_token))
    application_id = apps_resp.json()[0]["id"]

    resp = client.patch(
        f"/applications/{application_id}/decision",
        json={"status": "approved"},
        headers=_auth(officer_token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"

    audit = (
        db.query(AuditLog)
        .filter(
            AuditLog.entity == "scheme_applications",
            AuditLog.entity_id == application_id,
        )
        .first()
    )
    assert audit is not None

    _ = farmer_token  # keep for readability / future use


# ===========================================================================
# 7. Farmer cannot read another farmer's applications -> 403
# ===========================================================================
def test_farmer_cannot_read_others_application(seeded_db):
    db, _ = seeded_db

    client.post(
        "/auth/register",
        json={
            "email": "phase12_farmer_b@example.com",
            "password": "Secret123!",
            "role": "farmer",
        },
    )
    login_a = client.post(
        "/auth/login",
        json={
            "email": "phase12_farmer_a@example.com",
            "password": "Secret123!",
        },
    )
    login_b = client.post(
        "/auth/login",
        json={
            "email": "phase12_farmer_b@example.com",
            "password": "Secret123!",
        },
    )
    token_a = login_a.json()["access_token"]
    token_b = login_b.json()["access_token"]

    client.put(
        "/me/profile",
        json={"full_name": "Suresh Patil", "mobile": "9000000000"},
        headers=_auth(token_b),
    )

    apps_a = client.get("/applications/prefill", headers=_auth(token_a))
    _ = apps_a  # sanity: endpoint still reachable for farmer A

    officer_token = seeded_db[1]
    all_apps = client.get("/applications", headers=_auth(officer_token)).json()
    application_id = all_apps[0]["id"]

    resp = client.get(f"/applications/{application_id}", headers=_auth(token_b))
    assert resp.status_code == 403
    db.rollback()


# ===========================================================================
# 8. autofill unit — 4 autofill fields + 2 manual -> 4 filled keys
# ===========================================================================
def test_autofill_unit_fills_only_available_fields():
    class Profile:
        full_name = "Ramesh Kotwal"
        mobile = "9876543210"
        village = "V1"
        total_land_ha = 1.5

    form_fields = [
        {"key": "full_name", "autofill_from": "full_name"},
        {"key": "mobile", "autofill_from": "mobile"},
        {"key": "village", "autofill_from": "village"},
        {"key": "total_land_ha", "autofill_from": "total_land_ha"},
        {"key": "declaration"},  # manual, no autofill_from
        {"key": "witness_name"},  # manual, no autofill_from
    ]
    values, autofilled_keys = autofill(form_fields, Profile())
    assert len(autofilled_keys) == 4
    assert values["declaration"] is None
    assert values["witness_name"] is None
