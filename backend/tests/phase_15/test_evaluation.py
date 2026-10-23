"""
Phase 15 tests — Evaluation, SHAP & Final Polish.

Tests:
  1. GET /evaluation/metrics (admin token) returns f1, precision, recall,
     auto_link_rate, review_rate.
  2. All metrics are floats in [0, 1].
  3. F1 > 0.90 on a controlled ground-truth scenario (regression guard).
  4. top_shap_features returns <= 4 items with feature, value, shap_value.
  5. Non-admin token -> 403.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import Base, engine
from app.core.security import create_token, hash_password
from app.main import app
from app.models.clean_record import CleanRecord
from app.models.match_candidate import MatchCandidate
from app.models.source_record import SourceRecord
from app.models.user import User
from app.resolution import evaluation as evaluation_module
from app.resolution.evaluation import evaluate_resolution
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
    for table in ("match_candidates", "clean_records", "source_records"):
        db.execute(text(f"DELETE FROM {table}"))
    db.commit()

    source = SourceRecord(source_name="agristack", source_row_id="dummy", raw_json={})
    db.add(source)
    db.flush()

    # 10 candidate pairs (20 clean_records): 9 are true matches, 1 is a true non-match.
    # 8 true matches correctly auto_linked (TP), 1 true match left in review (FN),
    # 1 true non-match left in review (TN, excluded from precision/recall).
    truth_by_clean_id: dict[int, str] = {}
    pairs: list[tuple[int, int, str]] = []
    for i in range(10):
        a = CleanRecord(source_record_id=source.id, name_norm=f"a{i}")
        b = CleanRecord(source_record_id=source.id, name_norm=f"b{i}")
        db.add_all([a, b])
        db.flush()

        if i < 9:
            truth_by_clean_id[a.id] = f"TRUE_FARMER_{i}"
            truth_by_clean_id[b.id] = f"TRUE_FARMER_{i}"
        else:
            truth_by_clean_id[a.id] = "TRUE_FARMER_X"
            truth_by_clean_id[b.id] = "TRUE_FARMER_Y"

        decision = "auto_link" if i < 8 else "review"
        pairs.append((a.id, b.id, decision))

    for record_a, record_b, decision in pairs:
        db.add(
            MatchCandidate(
                record_a=record_a, record_b=record_b, score=0.9, decision=decision
            )
        )
    db.commit()

    admin_token = _token(db, "phase15_admin@example.com", "admin")
    officer_token = _token(db, "phase15_officer@example.com", "officer")

    yield db, truth_by_clean_id, admin_token, officer_token

    for table in ("match_candidates", "clean_records", "source_records"):
        db.execute(text(f"DELETE FROM {table}"))
    db.commit()
    db.close()


# ===========================================================================
# 1 & 2. GET /evaluation/metrics shape + range
# ===========================================================================
def test_evaluation_metrics_shape_and_range(seeded_db):
    _, _, admin_token, _ = seeded_db
    resp = client.get("/evaluation/metrics", headers=_auth(admin_token))
    assert resp.status_code == 200
    body = resp.json()
    assert set(body) == {"precision", "recall", "f1", "auto_link_rate", "review_rate"}
    for value in body.values():
        assert isinstance(value, float)
        assert 0.0 <= value <= 1.0


# ===========================================================================
# 3. F1 > 0.90 on the controlled scenario
# ===========================================================================
def test_f1_regression_guard(seeded_db, monkeypatch):
    db, truth_by_clean_id, _, _ = seeded_db
    monkeypatch.setattr(
        evaluation_module, "_clean_record_truth_map", lambda _db: truth_by_clean_id
    )

    metrics = evaluate_resolution(db)
    assert metrics.f1 > 0.90
    assert metrics.precision == 1.0  # 8 TP, 0 FP
    assert round(metrics.recall, 3) == round(8 / 9, 3)


# ===========================================================================
# 4. top_shap_features
# ===========================================================================
def test_top_shap_features_bounded():
    features = {
        "name_jw": 0.95,
        "same_mobile": 1,
        "dob_match": 1,
        "village_match": 1,
        "survey_match": 0,
    }
    result = top_shap_features(features)
    assert len(result) <= 4
    for sf in result:
        assert hasattr(sf, "feature")
        assert hasattr(sf, "value")
        assert hasattr(sf, "shap_value")


# ===========================================================================
# 5. Non-admin -> 403
# ===========================================================================
def test_non_admin_forbidden(seeded_db):
    _, _, _, officer_token = seeded_db
    resp = client.get("/evaluation/metrics", headers=_auth(officer_token))
    assert resp.status_code == 403
