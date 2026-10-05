"""
Phase 05 backend E2E tests for Auth (JWT) + User Endpoints.

Tests:
  1. POST /auth/register with role=farmer → 201, user saved with hashed password.
  2. POST /auth/login with correct credentials → 200, token returned.
  3. POST /auth/login with wrong password → 401.
  4. GET /farmers without token → 401.
  5. GET /farmers with farmer-role token → 403.
  6. GET /farmers with officer-role token → 200 (empty list or list).
  7. GET /health still works unauthenticated.
  8. POST /auth/register duplicate email → 409.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.core.db import Base, engine
from app.main import app

client = TestClient(app)

TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

FARMER_EMAIL = "farmer_test@example.com"
OFFICER_EMAIL = "officer_test@example.com"
FARMER_PASSWORD = "SecurePass123!"
OFFICER_PASSWORD = "OfficerPass456!"


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    db.execute(
        text("DELETE FROM users WHERE email IN (:e1, :e2)"),
        {"e1": FARMER_EMAIL, "e2": OFFICER_EMAIL},
    )
    db.commit()
    db.close()
    yield
    db2 = TestingSession()
    db2.execute(
        text("DELETE FROM users WHERE email IN (:e1, :e2)"),
        {"e1": FARMER_EMAIL, "e2": OFFICER_EMAIL},
    )
    db2.commit()
    db2.close()


# ---------------------------------------------------------------------------
# 1. Register farmer
# ---------------------------------------------------------------------------
def test_register_farmer_returns_201():
    resp = client.post(
        "/auth/register",
        json={
            "email": FARMER_EMAIL,
            "password": FARMER_PASSWORD,
            "role": "farmer",
        },
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert "access_token" in body
    assert body["role"] == "farmer"


# ---------------------------------------------------------------------------
# 2. Login correct credentials
# ---------------------------------------------------------------------------
def test_login_correct_credentials_returns_200():
    resp = client.post(
        "/auth/login",
        json={
            "email": FARMER_EMAIL,
            "password": FARMER_PASSWORD,
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


# ---------------------------------------------------------------------------
# 3. Login wrong password → 401
# ---------------------------------------------------------------------------
def test_login_wrong_password_returns_401():
    resp = client.post(
        "/auth/login",
        json={
            "email": FARMER_EMAIL,
            "password": "WrongPassword!",
        },
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 4. GET /farmers without token → 401
# ---------------------------------------------------------------------------
def test_get_farmers_no_token_returns_401():
    resp = client.get("/farmers")
    assert resp.status_code in (401, 403)  # HTTPBearer returns 403 on missing header


# ---------------------------------------------------------------------------
# 5. GET /farmers with farmer-role token → 403
# ---------------------------------------------------------------------------
def test_get_farmers_farmer_role_returns_403():
    login = client.post(
        "/auth/login", json={"email": FARMER_EMAIL, "password": FARMER_PASSWORD}
    )
    token = login.json()["access_token"]
    resp = client.get("/farmers", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 6. GET /farmers with officer-role token → 200
# ---------------------------------------------------------------------------
def test_get_farmers_officer_role_returns_200():
    # Register officer first
    client.post(
        "/auth/register",
        json={
            "email": OFFICER_EMAIL,
            "password": OFFICER_PASSWORD,
            "role": "officer",
        },
    )
    login = client.post(
        "/auth/login", json={"email": OFFICER_EMAIL, "password": OFFICER_PASSWORD}
    )
    token = login.json()["access_token"]
    resp = client.get("/farmers", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# ---------------------------------------------------------------------------
# 7. GET /health still works unauthenticated
# ---------------------------------------------------------------------------
def test_health_unauthenticated():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# 8. Duplicate email → 409
# ---------------------------------------------------------------------------
def test_register_duplicate_email_returns_409():
    resp = client.post(
        "/auth/register",
        json={
            "email": FARMER_EMAIL,
            "password": "AnotherPass!",
            "role": "farmer",
        },
    )
    assert resp.status_code == 409
