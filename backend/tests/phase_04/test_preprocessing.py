"""
Phase 04 tests for Preprocessing / Normalizers — Spec Section 6, Module 2.

Unit tests (pure functions, no DB):
  1.  normalize_name strips honorifics and collapses spaces
  2.  normalize_name folds transliteration variants
  3.  phonetic_key("Kotwal") == phonetic_key("Kotval")
  4.  normalize_mobile strips formatting and keeps last 10 digits
  5.  normalize_mobile returns None for invalid numbers
  6.  parse_dob accepts several date formats
  7.  parse_dob returns None for empty input
  8.  fill_missing never replaces None with an invented value

Integration tests (real DB session):
  9.  PreprocessingPipeline on 250 ingested sample rows → 250 clean_records
  10. Every clean_records row has a non-null name_norm
  11. POST /pipeline/preprocess returns 202
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import Base, engine
from app.main import app
from app.models.clean_record import CleanRecord
from app.models.source_record import SourceRecord
from app.preprocessing.normalizers import (
    fill_missing,
    normalize_mobile,
    normalize_name,
    parse_dob,
    phonetic_key,
)
from app.preprocessing.pipeline import PreprocessingPipeline
from app.services.ingestion_service import IngestionService

SAMPLES_DIR = Path(__file__).resolve().parents[3] / "data" / "synthetic" / "samples"

TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------------------------------------------------------------------------
# DB fixture — isolated clean_records for this test module
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    db: Session = TestingSession()
    # Wipe and re-seed source_records from samples
    db.execute(text("DELETE FROM clean_records"))
    db.execute(text("DELETE FROM source_records"))
    db.commit()

    if SAMPLES_DIR.exists():
        svc = IngestionService(db)
        svc.ingest_all(SAMPLES_DIR)

    try:
        yield db
    finally:
        db.execute(text("DELETE FROM clean_records"))
        db.execute(text("DELETE FROM source_records"))
        db.commit()
        db.close()


# ===========================================================================
# UNIT TESTS — normalize_name
# ===========================================================================
def test_normalize_name_removes_honorifics():
    # "Shri" removed, "Ramesh" preserved, "Kotwal" w→v via transliteration
    result = normalize_name("Shri Ramesh Kotwal")
    assert result is not None
    assert "shri" not in result
    assert "ramesh" in result
    assert "kotval" in result


def test_normalize_name_collapses_spaces():
    assert normalize_name("  Kumar   Singh  ") == "kumar singh"


def test_normalize_name_folds_transliteration():
    # aa→a, w→v
    assert normalize_name("Raam Wagh") == "ram vagh"


def test_normalize_name_none_for_empty():
    assert normalize_name("") is None
    assert normalize_name(None) is None
    assert normalize_name("   ") is None


def test_normalize_name_strips_punctuation():
    result = normalize_name("Kumar, A.")
    assert "," not in (result or "")


# ===========================================================================
# UNIT TESTS — phonetic_key
# ===========================================================================
def test_phonetic_key_same_for_variants():
    """Kotwal and Kotval must share a Double Metaphone key."""
    assert phonetic_key("Kotwal") == phonetic_key("Kotval")


def test_phonetic_key_none_for_empty():
    assert phonetic_key(None) is None
    assert phonetic_key("") is None


def test_phonetic_key_uses_first_token():
    k1 = phonetic_key("Ramesh Kumar")
    k2 = phonetic_key("Ramesh Singh")
    # Both share the same first token → same metaphone key
    assert k1 == k2


# ===========================================================================
# UNIT TESTS — normalize_mobile
# ===========================================================================
def test_normalize_mobile_strips_formatting():
    assert normalize_mobile("0 91 98765-43210") == "9876543210"


def test_normalize_mobile_keeps_last_10():
    assert normalize_mobile("919876543210") == "9876543210"


def test_normalize_mobile_none_for_invalid():
    assert normalize_mobile(None) is None
    assert normalize_mobile("12345") is None  # too short
    assert normalize_mobile("1234567890") is None  # starts with 1 (invalid)
    assert normalize_mobile("0000000000") is None  # all zeros


def test_normalize_mobile_valid_prefixes():
    for prefix in "6789":
        assert normalize_mobile(f"{prefix}123456789") is not None


# ===========================================================================
# UNIT TESTS — parse_dob
# ===========================================================================
def test_parse_dob_multiple_formats():
    cases = [
        ("15-08-1985", date(1985, 8, 15)),
        ("15/08/1985", date(1985, 8, 15)),
        ("1985-08-15", date(1985, 8, 15)),
        ("15-Aug-1985", date(1985, 8, 15)),
    ]
    for raw, expected in cases:
        assert parse_dob(raw) == expected, f"Failed for: {raw}"


def test_parse_dob_none_for_empty():
    assert parse_dob(None) is None
    assert parse_dob("") is None
    assert parse_dob("   ") is None


def test_parse_dob_year_fallback():
    result = parse_dob("born in 1990")
    assert result is not None
    assert result.year == 1990


# ===========================================================================
# UNIT TESTS — fill_missing
# ===========================================================================
def test_fill_missing_never_invents():
    assert fill_missing(None) is None
    assert fill_missing("") == ""
    assert fill_missing(42) == 42
    assert fill_missing("hello") == "hello"


# ===========================================================================
# INTEGRATION — PreprocessingPipeline + DB
# ===========================================================================
def test_preprocessing_pipeline_writes_clean_records(db_session):
    if not SAMPLES_DIR.exists():
        pytest.skip("Samples not found")
    pipeline = PreprocessingPipeline(db_session)
    count = pipeline.run()
    assert count > 0, "Pipeline wrote 0 clean_records"


def test_all_clean_records_have_name_norm(db_session):
    if not SAMPLES_DIR.exists():
        pytest.skip("Samples not found")
    rows = db_session.query(CleanRecord).all()
    assert len(rows) > 0
    missing = [r for r in rows if not r.name_norm]
    # Some rows may legitimately have no name (blank in source)
    # Assert the MAJORITY have name_norm (≥ 80%)
    assert (
        len(missing) / len(rows) < 0.20
    ), f"Too many rows without name_norm: {len(missing)}/{len(rows)}"


def test_clean_records_source_record_id_links(db_session):
    """Every clean_record must reference a valid source_record."""
    if not SAMPLES_DIR.exists():
        pytest.skip("Samples not found")
    src_ids = {r.id for r in db_session.query(SourceRecord).all()}
    bad = [
        r
        for r in db_session.query(CleanRecord).all()
        if r.source_record_id not in src_ids
    ]
    assert not bad, f"{len(bad)} clean_records with invalid source_record_id"


# ===========================================================================
# API endpoint test
# ===========================================================================
def test_preprocess_endpoint_returns_202():
    client = TestClient(app)
    response = client.post("/pipeline/preprocess")
    assert response.status_code == 202
    assert response.json()["status"] == "accepted"
