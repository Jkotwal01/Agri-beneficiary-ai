"""
Phase 08 tests — Duplicate Rules & Eligibility Engine.

Tests:
  1. SameSchemeTwice: High flag for two pmkisan enrollments same season.
  2. ParcelOverclaim: Medium flag when claims exceed parcel area.
  3. SharedBankAccount: detects shared-bank rows.
  4. LowConfidenceMerge: fires only when confidence < threshold.
  5. Eligibility: farmer with 0 land → PM_KISAN not eligible.
  6. Eligibility: farmer with 0.5 ha → PM_KISAN eligible.
  7. GET /flags?type=SameSchemeTwice&status=open → only matching flags.
  8. PATCH /flags/{id} with {"status": "confirmed"} updates DB + audit_log.
  9. POST /pipeline/evaluate → 202.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import Base, engine
from app.duplicates.rules.low_confidence_merge import LowConfidenceMerge
from app.duplicates.rules.parcel_overclaim import ParcelOverclaim
from app.duplicates.rules.same_scheme_twice import SameSchemeTwice
from app.duplicates.rules.shared_bank_account import SharedBankAccount
from app.eligibility.engine import evaluate
from app.main import app
from app.models.audit_log import AuditLog
from app.models.farmer import Farmer
from app.models.flag import Flag
from app.models.user import User

TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
client = TestClient(app)


# ===========================================================================
# 1. SameSchemeTwice
# ===========================================================================
def test_same_scheme_twice_raises_high_flag():
    rule = SameSchemeTwice()
    facts = {
        "enrollments": [
            {"scheme_id": 1, "season": "Kharif-2023", "scheme_name": "PMKISAN"},
            {"scheme_id": 1, "season": "Kharif-2023", "scheme_name": "PMKISAN"},
        ]
    }
    flags = rule.check(farmer_id=1, facts=facts)
    assert len(flags) >= 1
    assert flags[0].severity == "High"
    assert flags[0].rule == "SameSchemeTwice"


# ===========================================================================
# 2. ParcelOverclaim
# ===========================================================================
def test_parcel_overclaim_raises_medium_flag():
    rule = ParcelOverclaim()
    facts = {"total_land_ha": 1.0, "claimed_area_ha": 2.5}
    flags = rule.check(farmer_id=2, facts=facts)
    assert len(flags) == 1
    assert flags[0].severity == "Medium"
    assert flags[0].rule == "ParcelOverclaim"


def test_parcel_overclaim_no_flag_when_within_limit():
    rule = ParcelOverclaim()
    facts = {"total_land_ha": 2.0, "claimed_area_ha": 1.5}
    flags = rule.check(farmer_id=3, facts=facts)
    assert flags == []


# ===========================================================================
# 3. SharedBankAccount
# ===========================================================================
def test_shared_bank_account_detects_shared():
    rule = SharedBankAccount()
    facts = {"shared_bank_farmer_ids": [10, 11]}
    flags = rule.check(farmer_id=5, facts=facts)
    assert len(flags) == 1
    assert flags[0].rule == "SharedBankAccount"
    assert flags[0].severity == "High"


# ===========================================================================
# 4. LowConfidenceMerge
# ===========================================================================
def test_low_confidence_merge_fires_below_threshold():
    rule = LowConfidenceMerge(threshold=0.70)
    flags = rule.check(farmer_id=6, facts={"confidence": 0.55})
    assert len(flags) == 1
    assert flags[0].rule == "LowConfidenceMerge"


def test_low_confidence_merge_no_flag_above_threshold():
    rule = LowConfidenceMerge(threshold=0.70)
    flags = rule.check(farmer_id=7, facts={"confidence": 0.85})
    assert flags == []


# ===========================================================================
# 5. Eligibility: 0 land → PM_KISAN not eligible
# ===========================================================================
def test_eligibility_zero_land_not_eligible():
    result = evaluate("PM_KISAN", {"total_land_ha": 0, "crop": "wheat"})
    assert not result.eligible
    assert any("0" in r or "land" in r.lower() for r in result.reasons)


# ===========================================================================
# 6. Eligibility: 0.5 ha marginal farmer → PM_KISAN eligible
# ===========================================================================
def test_eligibility_marginal_farmer_eligible():
    result = evaluate("PM_KISAN", {"total_land_ha": 0.5, "crop": "wheat"})
    assert result.eligible
    assert result.reasons == []


# ===========================================================================
# 7. GET /flags with filters
# ===========================================================================
@pytest.fixture(scope="module")
def db_with_flags():
    Base.metadata.create_all(bind=engine)
    db: Session = TestingSession()
    # Seed a user (needed by audit_log FK) and a farmer
    db.execute(text("DELETE FROM audit_log"))
    db.execute(text("DELETE FROM recommendations"))
    db.execute(text("DELETE FROM flags"))
    db.execute(text("DELETE FROM land_parcels"))
    db.execute(text("DELETE FROM farmer_links"))
    db.execute(text("DELETE FROM farmers"))
    db.commit()

    user = db.query(User).filter(User.email == "test_officer@example.com").first()
    if not user:
        user = User(email="test_officer@example.com", password_hash="dummy", role="officer")
        db.add(user)
        db.flush()

    # Insert minimal farmer
    farmer = Farmer(name="Test", confidence=1.0)
    db.add(farmer)
    db.flush()

    flag1 = Flag(farmer_id=farmer.id, type="SameSchemeTwice",
                 severity="High", reason="duplicate", status="open")
    flag2 = Flag(farmer_id=farmer.id, type="ParcelOverclaim",
                 severity="Medium", reason="overclaim", status="open")
    db.add_all([flag1, flag2])
    db.commit()

    yield db, farmer.id, flag1.id

    db.execute(text("DELETE FROM audit_log"))
    db.execute(text("DELETE FROM recommendations"))
    db.execute(text("DELETE FROM flags"))
    db.execute(text("DELETE FROM land_parcels"))
    db.execute(text("DELETE FROM farmer_links"))
    db.execute(text("DELETE FROM farmers"))
    db.commit()
    db.close()


def test_get_flags_filtered(db_with_flags):
    resp = client.get("/flags?type=SameSchemeTwice&status=open")
    assert resp.status_code == 200
    data = resp.json()
    assert all(f["type"] == "SameSchemeTwice" for f in data)
    assert all(f["status"] == "open" for f in data)
    assert len(data) >= 1


# ===========================================================================
# 8. PATCH /flags/{id} updates status + writes audit_log
# ===========================================================================
def test_patch_flag_status(db_with_flags):
    db, _farmer_id, flag_id = db_with_flags
    resp = client.patch(f"/flags/{flag_id}", json={"status": "confirmed"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"

    # Verify audit_log written
    db.expire_all()
    log = db.query(AuditLog).filter(
        AuditLog.entity == "flags",
        AuditLog.entity_id == flag_id,
    ).first()
    assert log is not None
    assert "confirmed" in log.action


# ===========================================================================
# 9. POST /pipeline/evaluate → 202
# ===========================================================================
def test_evaluate_endpoint_returns_202():
    resp = client.post("/pipeline/evaluate")
    assert resp.status_code == 202
    assert resp.json()["status"] == "accepted"
