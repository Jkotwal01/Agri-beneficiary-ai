"""
Phase 06 tests — Blocking & Pair Feature Extraction.
Spec Section 6, Module 3, Stages 1 & 2.

Tests:
  1.  Two records sharing district_code + name_phonetic → candidate pair.
  2.  Two records sharing mobile10 → candidate pair.
  3.  Two records sharing village_code + survey_no → candidate pair.
  4.  Two completely unrelated records → NOT a candidate pair.
  5.  Reduction ratio: blocking on 250-row sample generates < 2,500 pairs.
  6.  Pair completeness: planted true-match pairs are recovered by the blocker.
  7.  name_jw is in [0,1] for valid inputs.
  8.  same_mobile is 1/0/−1 for match / mismatch / null.
  9.  father_name_sim is −1 when either value is null.
  10. Phonetic match: same phonetic key → phonetic_match=1.
  11. Blocking on 5,000 synthetic records runs in < 10 seconds.
"""

from __future__ import annotations

import time

import pytest

from app.resolution.blocking import PhoneticVillageBlocker, Record
from app.resolution.features import build_feature_vector


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def make_record(**kwargs) -> Record:
    """Create a Record with sensible defaults for optional fields."""
    defaults = {
        "id": 1,
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
    defaults.update(kwargs)
    return Record(**defaults)


blocker = PhoneticVillageBlocker()


# ===========================================================================
# BLOCKING TESTS
# ===========================================================================


# 1. Key 1: district_code + name_phonetic
def test_key1_district_phonetic_produces_pair():
    r1 = make_record(id=1, district_code="D01", name_phonetic="KTFL")
    r2 = make_record(id=2, district_code="D01", name_phonetic="KTFL")
    r3 = make_record(id=3, district_code="D99", name_phonetic="ABCD")
    pairs = blocker.candidate_pairs([r1, r2, r3])
    assert (1, 2) in pairs
    assert (1, 3) not in pairs
    assert (2, 3) not in pairs


# 2. Key 2: mobile10
def test_key2_mobile_produces_pair():
    r1 = make_record(id=10, mobile10="9876543210")
    r2 = make_record(id=11, mobile10="9876543210")
    r3 = make_record(id=12, mobile10="8888888888")
    pairs = blocker.candidate_pairs([r1, r2, r3])
    assert (10, 11) in pairs
    assert (10, 12) not in pairs


# 3. Key 3: village_code + survey_no
def test_key3_village_survey_produces_pair():
    r1 = make_record(id=20, village_code="V001", survey_no="SRV-42")
    r2 = make_record(id=21, village_code="V001", survey_no="SRV-42")
    r3 = make_record(id=22, village_code="V002", survey_no="SRV-42")
    pairs = blocker.candidate_pairs([r1, r2, r3])
    assert (20, 21) in pairs
    assert (20, 22) not in pairs


# 4. Completely unrelated records → no pair
def test_unrelated_records_not_paired():
    r1 = make_record(
        id=30,
        district_code="D01",
        name_phonetic="KTFL",
        mobile10="9111111111",
        village_code="V001",
        survey_no="S1",
    )
    r2 = make_record(
        id=31,
        district_code="D99",
        name_phonetic="XYZW",
        mobile10="9222222222",
        village_code="V999",
        survey_no="S9",
    )
    pairs = blocker.candidate_pairs([r1, r2])
    assert len(pairs) == 0


# 5. Reduction ratio on 250 records < 2,500 pairs
def test_reduction_ratio_250_rows():
    import random

    rng = random.Random(42)
    records = [
        make_record(
            id=i,
            district_code=rng.choice(["D01", "D02", "D03", "D04", "D05"]),
            name_phonetic=rng.choice(["KTFL", "RMSH", "SNGH", "PNDX", "GPTX"]),
            mobile10=str(rng.randint(6_000_000_000, 9_999_999_999)),
            village_code=rng.choice(["V001", "V002", "V003", "V004", "V005"]),
            survey_no=rng.choice(["S1", "S2", "S3", "S4", "S5"]),
        )
        for i in range(250)
    ]
    pairs = blocker.candidate_pairs(records)
    assert len(pairs) < 2500, f"Too many pairs: {len(pairs)}"


# 6. Pair completeness — planted true matches are recovered
def test_planted_true_matches_recovered():
    """
    Plant 5 true-match pairs with identical blocking keys and verify
    each pair appears in the candidate output.
    """
    true_pairs = []
    records = []
    base_id = 100
    for i in range(5):
        r1 = make_record(
            id=base_id + i * 2,
            district_code="D01",
            name_phonetic=f"PH0{i}",
            mobile10=f"9{i:09d}",
        )
        r2 = make_record(
            id=base_id + i * 2 + 1,
            district_code="D01",
            name_phonetic=f"PH0{i}",
            mobile10=f"9{i:09d}",
        )
        records.extend([r1, r2])
        pair = (min(r1.id, r2.id), max(r1.id, r2.id))
        true_pairs.append(pair)

    pairs = set(blocker.candidate_pairs(records))
    for tp in true_pairs:
        assert tp in pairs, f"True match pair {tp} was not recovered by blocker"


# ===========================================================================
# FEATURE VECTOR TESTS
# ===========================================================================


# 7. name_jw in [0, 1]
def test_name_jw_range():
    a = make_record(id=1, name_norm="ramesh kumar")
    b = make_record(id=2, name_norm="ramesh singh")
    fv = build_feature_vector(a, b)
    assert 0.0 <= fv["name_jw"] <= 1.0


def test_name_jw_exact_match():
    a = make_record(id=1, name_norm="ramesh kumar")
    b = make_record(id=2, name_norm="ramesh kumar")
    fv = build_feature_vector(a, b)
    assert fv["name_jw"] == pytest.approx(1.0)


def test_name_jw_missing_is_zero():
    a = make_record(id=1, name_norm=None)
    b = make_record(id=2, name_norm="ramesh kumar")
    fv = build_feature_vector(a, b)
    assert fv["name_jw"] == 0.0


# 8. same_mobile is 1 / 0 / −1
def test_same_mobile_match():
    a = make_record(id=1, mobile10="9876543210")
    b = make_record(id=2, mobile10="9876543210")
    fv = build_feature_vector(a, b)
    assert fv["same_mobile"] == 1


def test_same_mobile_mismatch():
    a = make_record(id=1, mobile10="9876543210")
    b = make_record(id=2, mobile10="9000000000")
    fv = build_feature_vector(a, b)
    assert fv["same_mobile"] == 0


def test_same_mobile_null():
    a = make_record(id=1, mobile10=None)
    b = make_record(id=2, mobile10="9876543210")
    fv = build_feature_vector(a, b)
    assert fv["same_mobile"] == -1


# 9. father_name_sim is −1 when either is null
def test_father_name_sim_null():
    a = make_record(id=1, father_norm="ramesh")
    b = make_record(id=2, father_norm=None)
    fv = build_feature_vector(a, b)
    assert fv["father_name_sim"] == -1.0


def test_father_name_sim_valid():
    a = make_record(id=1, father_norm="ramesh lal")
    b = make_record(id=2, father_norm="ramesh lal")
    fv = build_feature_vector(a, b)
    assert fv["father_name_sim"] == pytest.approx(1.0)


# 10. phonetic_match
def test_phonetic_match_same():
    a = make_record(id=1, name_phonetic="KTFL")
    b = make_record(id=2, name_phonetic="KTFL")
    fv = build_feature_vector(a, b)
    assert fv["phonetic_match"] == 1


def test_phonetic_match_differ():
    a = make_record(id=1, name_phonetic="KTFL")
    b = make_record(id=2, name_phonetic="RMSH")
    fv = build_feature_vector(a, b)
    assert fv["phonetic_match"] == 0


# ===========================================================================
# PERFORMANCE TEST — 5,000 records in < 10 s
# ===========================================================================
def test_blocking_5000_records_under_10s():
    import random

    rng = random.Random(0)
    records = [
        make_record(
            id=i,
            district_code=rng.choice([f"D{d:02d}" for d in range(20)]),
            name_phonetic=rng.choice(
                [
                    "KTFL",
                    "RMSH",
                    "SNGH",
                    "PNDX",
                    "GPTX",
                    "VRMA",
                    "JNSH",
                    "BKSH",
                    "YDVX",
                    "MSHR",
                ]
            ),
            mobile10=str(rng.randint(6_000_000_000, 9_999_999_999)),
            village_code=rng.choice([f"V{v:03d}" for v in range(50)]),
            survey_no=rng.choice([f"S{s}" for s in range(30)]),
        )
        for i in range(5000)
    ]
    start = time.perf_counter()
    pairs = blocker.candidate_pairs(records)
    elapsed = time.perf_counter() - start
    assert elapsed < 10.0, f"Blocking took {elapsed:.2f}s — too slow"
    assert len(pairs) > 0
