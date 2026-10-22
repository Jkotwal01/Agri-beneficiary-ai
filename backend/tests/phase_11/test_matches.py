"""
Phase 11 tests — Review Queue & Match Decision Backend.

Tests:
  1. GET /matches?decision=review returns only review-decision pairs.
  2. POST /matches/{id}/decision {confirm} -> decision=manual_link, audit_log written.
  3. POST /matches/{id}/decision {reject} -> decision=no_match.
  4. Non-officer token -> 403.
  5. GET /farmers/{id} returns full payload: linked records, enrollments, flags, recommendations.
  6. top_shap_features(features) returns <= 4 ShapFeature objects with feature, value, shap_value.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import Base, engine
from app.core.security import create_token, hash_password
from app.main import app
from app.models.audit_log import AuditLog
from app.models.clean_record import CleanRecord
from app.models.enrollment import Enrollment
from app.models.farmer import Farmer
from app.models.farmer_link import FarmerLink
from app.models.flag import Flag
from app.models.match_candidate import MatchCandidate
from app.models.recommendation import Recommendation
from app.models.scheme import Scheme
from app.models.source_record import SourceRecord
from app.models.user import User
from app.resolution.explainability import top_shap_features

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
        "audit_log",
        "recommendations",
        "flags",
        "enrollments",
        "farmer_links",
        "match_candidates",
        "clean_records",
        "source_records",
        "farmers",
        "schemes",
    ):
        db.execute(text(f"DELETE FROM {table}"))
    db.commit()

    scheme = Scheme(code="PM_KISAN", name="PM_KISAN", benefit_score=10)
    db.add(scheme)
    db.flush()

    farmer = Farmer(
        name="Ramesh Kotwal", district_code="PUNE", village_code="V1", confidence=0.95
    )
    db.add(farmer)
    db.flush()

    source = SourceRecord(source_name="agristack", source_row_id="1", raw_json={"a": 1})
    db.add(source)
    db.flush()

    clean_a = CleanRecord(
        source_record_id=source.id,
        name_norm="ramesh kotwal",
        mobile10="9876543210",
        district_code="PUNE",
        village_code="V1",
        dob="1985-05-12",
    )
    clean_b = CleanRecord(
        source_record_id=source.id,
        name_norm="ramesh k",
        mobile10="9876543210",
        district_code="PUNE",
        village_code="V1",
        dob="1985-05-12",
    )
    db.add_all([clean_a, clean_b])
    db.flush()

    match_review = MatchCandidate(
        record_a=clean_a.id,
        record_b=clean_b.id,
        score=0.72,
        decision="review",
        features_json={
            "name_jw": 0.88,
            "same_mobile": 1,
            "dob_match": 1,
            "village_match": 1,
        },
    )
    match_linked = MatchCandidate(
        record_a=clean_a.id,
        record_b=clean_b.id,
        score=0.99,
        decision="auto_link",
        features_json={"name_jw": 1.0, "same_mobile": 1},
    )
    db.add_all([match_review, match_linked])
    db.flush()

    db.add(
        FarmerLink(
            farmer_id=farmer.id, clean_record_id=clean_a.id, method="rule", score=1.0
        )
    )
    db.add(
        Enrollment(
            farmer_id=farmer.id,
            scheme_id=scheme.id,
            season="Kharif-2023",
            amount=2000.0,
        )
    )
    db.add(
        Flag(
            farmer_id=farmer.id,
            type="SameSchemeTwice",
            severity="High",
            reason="dup",
            status="open",
        )
    )
    db.add(
        Recommendation(
            farmer_id=farmer.id,
            scheme_id=scheme.id,
            eligible=True,
            already_enrolled=False,
            reasons_json=[],
            priority=1,
        )
    )
    db.commit()

    officer_token = _token(db, "phase11_officer@example.com", "officer")
    farmer_token = _token(db, "phase11_farmer@example.com", "farmer")

    yield db, farmer.id, match_review.id, officer_token, farmer_token

    for table in (
        "audit_log",
        "recommendations",
        "flags",
        "enrollments",
        "farmer_links",
        "match_candidates",
        "clean_records",
        "source_records",
        "farmers",
        "schemes",
    ):
        db.execute(text(f"DELETE FROM {table}"))
    db.commit()
    db.close()


# ===========================================================================
# 1. GET /matches?decision=review
# ===========================================================================
def test_list_matches_filtered_by_decision(seeded_db):
    _, _, _, officer_token, _ = seeded_db
    resp = client.get("/matches?decision=review", headers=_auth(officer_token))
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["decision"] == "review"
    assert body[0]["record_a"]["name_norm"] == "ramesh kotwal"


# ===========================================================================
# 2. POST /matches/{id}/decision {confirm}
# ===========================================================================
def test_confirm_decision_writes_manual_link_and_audit_log(seeded_db):
    db, _, match_id, officer_token, _ = seeded_db
    resp = client.post(
        f"/matches/{match_id}/decision",
        json={"decision": "confirm"},
        headers=_auth(officer_token),
    )
    assert resp.status_code == 200
    assert resp.json()["decision"] == "manual_link"

    audit = (
        db.query(AuditLog)
        .filter(AuditLog.entity == "match_candidates", AuditLog.entity_id == match_id)
        .first()
    )
    assert audit is not None
    assert "manual_link" in audit.action


# ===========================================================================
# 3. POST /matches/{id}/decision {reject}
# ===========================================================================
def test_reject_decision_sets_no_match(seeded_db):
    _, _, match_id, officer_token, _ = seeded_db
    resp = client.post(
        f"/matches/{match_id}/decision",
        json={"decision": "reject"},
        headers=_auth(officer_token),
    )
    assert resp.status_code == 200
    assert resp.json()["decision"] == "no_match"


# ===========================================================================
# 4. Non-officer token -> 403
# ===========================================================================
def test_non_officer_forbidden(seeded_db):
    _, _, match_id, _, farmer_token = seeded_db
    resp = client.get("/matches", headers=_auth(farmer_token))
    assert resp.status_code == 403
    resp2 = client.post(
        f"/matches/{match_id}/decision",
        json={"decision": "confirm"},
        headers=_auth(farmer_token),
    )
    assert resp2.status_code == 403


# ===========================================================================
# 5. GET /farmers/{id} full payload
# ===========================================================================
def test_farmer_detail_full_payload(seeded_db):
    _, farmer_id, _, officer_token, _ = seeded_db
    resp = client.get(f"/farmers/{farmer_id}", headers=_auth(officer_token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == farmer_id
    assert len(body["linked_records"]) == 1
    assert len(body["enrollments"]) == 1
    assert len(body["flags"]) == 1
    assert len(body["recommendations"]) == 1
    assert body["recommendations"][0]["scheme_code"] == "PM_KISAN"


# ===========================================================================
# 6. top_shap_features
# ===========================================================================
def test_top_shap_features_shape():
    features = {
        "name_jw": 0.88,
        "same_mobile": 1,
        "dob_match": 1,
        "village_match": 1,
        "survey_match": -1,
    }
    result = top_shap_features(features)
    assert len(result) <= 4
    for sf in result:
        assert hasattr(sf, "feature")
        assert hasattr(sf, "value")
        assert hasattr(sf, "shap_value")
