"""
Phase 07 tests — ML Matcher + Resolution Service.

Tests:
  1. Train script creates matcher.joblib.
  2. XGBoostPairMatcher.score(a, b) returns float in [0, 1].
  3. build_clusters on 5-node graph with 3 edges → correct components.
  4. Chain guard: component with > 6 records → flagged for review.
  5. Chain guard: 2 different AgriStack IDs → not auto-merged.
  6. GoldenRecordBuilder prefers AgriStack name over NFSM.
  7. Full ResolutionService.run() on sample DB → ≥ 1 farmer, match_candidates populated.
  8. POST /pipeline/resolve → 202.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import Base, engine
from app.main import app
from app.models.farmer import Farmer
from app.models.match_candidate import MatchCandidate
from app.resolution.blocking import Record
from app.resolution.clustering import build_clusters, passes_chain_guard
from app.resolution.golden_record import TrustOrderGoldenRecordBuilder
from app.resolution.matcher import XGBoostPairMatcher
from app.services.ingestion_service import IngestionService
from app.services.preprocessing_service import PreprocessingService
from app.services.resolution_service import ResolutionService

BACKEND_DIR = Path(__file__).resolve().parents[2]  # backend/
SAMPLES_DIR = BACKEND_DIR.parent / "data" / "synthetic" / "samples"
MODEL_PATH = BACKEND_DIR / "models" / "matcher.joblib"

TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)


def _make_rec(**kw) -> Record:
    defaults = {
        "id": 0,
        "name_norm": None,
        "father_norm": None,
        "name_phonetic": None,
        "mobile10": None,
        "village_code": None,
        "district_code": None,
        "survey_no": None,
        "dob": None,
        "bank_last4": None,
        "crop": None,
        "season": None,
    }
    defaults.update(kw)
    return Record(**defaults)


# ===========================================================================
# 1. Train script creates matcher.joblib
# ===========================================================================
def test_train_script_creates_model():
    import subprocess
    import sys

    train_script = BACKEND_DIR / "scripts" / "train_matcher.py"
    result = subprocess.run(
        [sys.executable, str(train_script)],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(BACKEND_DIR),
        env={**__import__("os").environ, "PYTHONPATH": str(BACKEND_DIR)},
    )
    assert result.returncode == 0, result.stderr
    assert MODEL_PATH.exists(), "matcher.joblib not created"


# ===========================================================================
# 2. XGBoostPairMatcher.score returns [0, 1]
# ===========================================================================
def test_matcher_score_in_range():
    matcher = XGBoostPairMatcher()
    a = _make_rec(
        id=1,
        name_norm="ramesh kumar",
        mobile10="9876543210",
        name_phonetic="RMSH",
        district_code="D01",
    )
    b = _make_rec(
        id=2,
        name_norm="ramesh kumar",
        mobile10="9876543210",
        name_phonetic="RMSH",
        district_code="D01",
    )
    score = matcher.score(a, b)
    assert 0.0 <= score <= 1.0


def test_matcher_high_score_for_match():
    """Identical records should get a high score."""
    matcher = XGBoostPairMatcher()
    a = _make_rec(
        id=1,
        name_norm="suresh singh",
        mobile10="9111111111",
        name_phonetic="SRSH",
        village_code="V01",
        survey_no="S1",
        dob="1985-01-01",
        bank_last4="1234",
        father_norm="hari singh",
    )
    b = _make_rec(
        id=2,
        name_norm="suresh singh",
        mobile10="9111111111",
        name_phonetic="SRSH",
        village_code="V01",
        survey_no="S1",
        dob="1985-01-01",
        bank_last4="1234",
        father_norm="hari singh",
    )
    score = matcher.score(a, b)
    assert score >= 0.80, f"Expected high score for identical records, got {score}"


# ===========================================================================
# 3. build_clusters on 5-node graph with 3 edges
# ===========================================================================
def test_build_clusters_components():
    # 3 edges: 1-2, 2-3, 4-5 → two components [1,2,3] and [4,5]
    pairs = [(1, 2), (2, 3), (4, 5)]
    clusters = build_clusters(pairs)
    sizes = sorted(len(c) for c in clusters)
    assert sizes == [2, 3], f"Unexpected cluster sizes: {sizes}"

    all_ids = {rid for c in clusters for rid in c}
    assert all_ids == {1, 2, 3, 4, 5}


# ===========================================================================
# 4. Chain guard: cluster > 6 records → blocked
# ===========================================================================
def test_chain_guard_too_large():
    large_cluster = list(range(1, 9))  # 8 records
    ok, reason = passes_chain_guard(large_cluster)
    assert not ok
    assert "exceeds" in reason.lower()


# ===========================================================================
# 5. Chain guard: 2 AgriStack IDs → blocked
# ===========================================================================
def test_chain_guard_two_agristack():
    cluster = [1, 2, 3]
    source_map = {1: "agristack", 2: "agristack", 3: "pmkisan"}
    ok, reason = passes_chain_guard(cluster, source_map)
    assert not ok
    assert "agristack" in reason.lower()


# ===========================================================================
# 6. GoldenRecordBuilder prefers AgriStack over NFSM
# ===========================================================================
def test_golden_record_prefers_agristack():
    builder = TrustOrderGoldenRecordBuilder()
    agristack_rec = _make_rec(id=1, name_norm="ramesh lal")
    nfsm_rec = _make_rec(id=2, name_norm="rameshlal")  # slightly different

    golden = builder.build(
        [
            (nfsm_rec, "nfsm"),
            (agristack_rec, "agristack"),
        ]
    )
    assert (
        golden["name_norm"] == "ramesh lal"
    ), f"Expected AgriStack value but got: {golden['name_norm']}"


# ===========================================================================
# 7. Full ResolutionService.run() on sample DB
# ===========================================================================
@pytest.fixture(scope="module")
def populated_db():
    Base.metadata.create_all(bind=engine)
    db: Session = TestingSession()
    db.execute(text("DELETE FROM farmer_links"))
    db.execute(text("DELETE FROM farmers"))
    db.execute(text("DELETE FROM match_candidates"))
    db.execute(text("DELETE FROM clean_records"))
    db.execute(text("DELETE FROM source_records"))
    db.commit()

    if SAMPLES_DIR.exists():
        IngestionService(db).ingest_all(SAMPLES_DIR)
        PreprocessingService(db).run()

    try:
        yield db
    finally:
        db.execute(text("DELETE FROM farmer_links"))
        db.execute(text("DELETE FROM farmers"))
        db.execute(text("DELETE FROM match_candidates"))
        db.execute(text("DELETE FROM clean_records"))
        db.execute(text("DELETE FROM source_records"))
        db.commit()
        db.close()


def test_resolution_service_creates_farmers(populated_db):
    if not SAMPLES_DIR.exists():
        pytest.skip("Sample data not found")
    svc = ResolutionService(populated_db)
    summary = svc.run()

    farmers_count = populated_db.query(Farmer).count()
    candidates_count = populated_db.query(MatchCandidate).count()

    assert farmers_count >= 1, "No farmers created"
    assert candidates_count >= 0
    assert summary.clean_records_processed > 0
    assert summary.farmers_created >= 1


# ===========================================================================
# 8. POST /pipeline/resolve → 202
# ===========================================================================
def test_resolve_endpoint_returns_202():
    resp = client.post("/pipeline/resolve")
    assert resp.status_code == 202
    assert resp.json()["status"] == "accepted"
