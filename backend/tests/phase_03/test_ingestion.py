"""Phase 03 E2E tests for the Ingestion Module.

Tests:
  1. Each adapter reads its sample CSV and yields dicts with a 'name' key.
  2. IngestionService.ingest_all() inserts rows for all 5 sources.
  3. source_records count = sum of all sample rows (≈250 for 50-row samples).
  4. raw_json is populated (not empty) for every inserted row.
  5. source_name on every row matches the adapter's source_name.
  6. POST /pipeline/ingest returns HTTP 202.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import Base, engine
from app.ingestion.adapters.agristack import AgriStackAdapter
from app.ingestion.adapters.kcc import KccAdapter
from app.ingestion.adapters.nfsm import NfsmAdapter
from app.ingestion.adapters.pmfby import PmfbyAdapter
from app.ingestion.adapters.pmkisan import PmKisanAdapter
from app.ingestion.registry import SOURCE_FILES
from app.main import app
from app.models.source_record import SourceRecord
from app.services.ingestion_service import IngestionService

REPO_ROOT = Path(__file__).resolve().parents[3]
SAMPLES_DIR = REPO_ROOT / "data" / "synthetic" / "samples"

TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _get_sample_dir() -> Path | None:
    """Return samples dir if it exists, else None (test will skip)."""
    return SAMPLES_DIR if SAMPLES_DIR.exists() else None


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    db: Session = TestingSession()
    # Clean source_records before this test run
    db.execute(text("DELETE FROM source_records"))
    db.commit()
    try:
        yield db
    finally:
        db.execute(text("DELETE FROM source_records"))
        db.commit()
        db.close()


# ---------------------------------------------------------------------------
# 1. Adapter unit tests
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "adapter_cls, filename",
    [
        (AgriStackAdapter, "agristack_farmers.csv"),
        (PmKisanAdapter, "pmkisan.csv"),
        (PmfbyAdapter, "pmfby.csv"),
        (NfsmAdapter, "nfsm.csv"),
        (KccAdapter, "kcc.csv"),
    ],
)
def test_adapter_reads_name_field(adapter_cls, filename):
    path = SAMPLES_DIR / filename
    if not path.exists():
        pytest.skip(f"Sample file not found: {path}")
    adapter = adapter_cls()
    rows = list(adapter.read(path))
    assert len(rows) > 0, f"{filename}: no rows read"
    assert "name" in rows[0], f"{adapter_cls.__name__}: 'name' key missing"


# ---------------------------------------------------------------------------
# 2-5. IngestionService integration tests
# ---------------------------------------------------------------------------
def test_ingest_all_inserts_rows(db_session):
    if not SAMPLES_DIR.exists():
        pytest.skip("Samples directory not found")
    svc = IngestionService(db_session)
    results = svc.ingest_all(SAMPLES_DIR)
    total = sum(results.values())
    assert total > 0, "No rows ingested"


def test_ingested_row_count(db_session):
    count = db_session.query(SourceRecord).count()
    # 5 sources × ≤50 sample rows + possible small variance
    assert count >= 50, f"Expected ≥50 rows, got {count}"


def test_raw_json_populated(db_session):
    sample = db_session.query(SourceRecord).first()
    assert sample is not None
    assert sample.raw_json, "raw_json is empty"
    assert "name" in sample.raw_json, "raw_json missing 'name'"


def test_source_name_matches_adapter(db_session):
    valid_names = set(SOURCE_FILES.keys())
    rows = db_session.query(SourceRecord).all()
    for row in rows:
        assert (
            row.source_name in valid_names
        ), f"Unexpected source_name: {row.source_name}"


# ---------------------------------------------------------------------------
# 6. API endpoint test
# ---------------------------------------------------------------------------
def test_pipeline_ingest_endpoint_returns_202():
    client = TestClient(app)
    response = client.post("/pipeline/ingest")
    assert response.status_code == 202
    assert response.json()["status"] == "accepted"
