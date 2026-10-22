"""
Phase 09 tests — Recommendations, Exclusions & Report Endpoints.

Tests:
  1. GET /reports/summary returns total_records, unique_farmers, open_flags, exclusions.
  2. GET /reports/coverage?group_by=district returns list with district + count + scheme_coverage.
  3. GET /reports/export?type=exclusions returns CSV content-type.
  4. GET /exclusions?district=&scheme= filters correctly.
  5. GET /recommendations?farmer_id=<id> returns eligible and not-enrolled schemes.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import Base, engine
from app.core.security import create_token, hash_password
from app.main import app
from app.models.farmer import Farmer
from app.models.flag import Flag
from app.models.recommendation import Recommendation
from app.models.scheme import Scheme
from app.models.source_record import SourceRecord
from app.models.user import User

TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
client = TestClient(app)


def _officer_token(db: Session) -> str:
    user = db.query(User).filter(User.email == "phase09_officer@example.com").first()
    if not user:
        user = User(
            email="phase09_officer@example.com",
            password_hash=hash_password("Secret123!"),
            role="officer",
        )
        db.add(user)
        db.flush()
        db.commit()
    return create_token({"sub": str(user.id)})


@pytest.fixture(scope="module")
def seeded_db():
    Base.metadata.create_all(bind=engine)
    db: Session = TestingSession()

    for table in ("recommendations", "flags", "source_records", "farmers", "schemes"):
        db.execute(text(f"DELETE FROM {table}"))
    db.commit()

    scheme = Scheme(code="PM_KISAN", name="PM_KISAN", benefit_score=10)
    db.add(scheme)
    db.flush()

    farmer_a = Farmer(name="Ramesh Kotwal", district_code="PUNE", village_code="V1", confidence=0.95)
    farmer_b = Farmer(name="Suresh Patil", district_code="NASHIK", village_code="V2", confidence=0.9)
    db.add_all([farmer_a, farmer_b])
    db.flush()

    db.add(SourceRecord(source_name="pmkisan", source_row_id="1", raw_json={"a": 1}))
    db.add(Flag(farmer_id=farmer_a.id, type="SameSchemeTwice", severity="High",
                reason="dup", status="open"))

    db.add(Recommendation(
        farmer_id=farmer_a.id, scheme_id=scheme.id,
        eligible=True, already_enrolled=False, reasons_json=[], priority=1,
    ))
    db.add(Recommendation(
        farmer_id=farmer_b.id, scheme_id=scheme.id,
        eligible=False, already_enrolled=False, reasons_json=["0 land"], priority=0,
    ))
    db.commit()

    token = _officer_token(db)

    yield db, farmer_a.id, scheme.id, token

    for table in ("recommendations", "flags", "source_records", "farmers", "schemes"):
        db.execute(text(f"DELETE FROM {table}"))
    db.commit()
    db.close()


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ===========================================================================
# 1. GET /reports/summary
# ===========================================================================
def test_reports_summary(seeded_db):
    _, _, _, token = seeded_db
    resp = client.get("/reports/summary", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert set(body) == {"total_records", "unique_farmers", "open_flags", "exclusions"}
    assert body["unique_farmers"] == 2
    assert body["open_flags"] == 1
    assert body["exclusions"] == 1


# ===========================================================================
# 2. GET /reports/coverage?group_by=district
# ===========================================================================
def test_reports_coverage_by_district(seeded_db):
    _, _, _, token = seeded_db
    resp = client.get("/reports/coverage?group_by=district", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    districts = {row["group"] for row in body}
    assert {"PUNE", "NASHIK"}.issubset(districts)
    for row in body:
        assert "count" in row and "scheme_coverage" in row


# ===========================================================================
# 3. GET /reports/export?type=exclusions
# ===========================================================================
def test_reports_export_exclusions_csv(seeded_db):
    _, _, _, token = seeded_db
    resp = client.get("/reports/export?type=exclusions", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert "farmer_id" in resp.text


# ===========================================================================
# 4. GET /exclusions?district=&scheme=
# ===========================================================================
def test_exclusions_filtered(seeded_db):
    _, farmer_a_id, _, token = seeded_db
    resp = client.get("/exclusions?district=PUNE&scheme=PM_KISAN", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["farmer_id"] == farmer_a_id
    assert body[0]["scheme_code"] == "PM_KISAN"

    resp_empty = client.get("/exclusions?district=NAGPUR", headers=_auth(token))
    assert resp_empty.json() == []


# ===========================================================================
# 5. GET /recommendations?farmer_id=<id>
# ===========================================================================
def test_recommendations_by_farmer(seeded_db):
    _, farmer_a_id, scheme_id, token = seeded_db
    resp = client.get(f"/recommendations?farmer_id={farmer_a_id}", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["farmer_id"] == farmer_a_id
    assert body[0]["scheme_id"] == scheme_id
    assert body[0]["eligible"] is True
