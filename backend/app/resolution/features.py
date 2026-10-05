"""
Pair Feature Extraction — Spec Section 6, Module 3, Stage 2.

build_feature_vector(a, b) → dict with 8 features:

  1. name_jw          float [0,1]   Jaro-Winkler similarity of name_norm
  2. father_name_sim  float         Jaro-Winkler of father_norm; -1 if either is null
  3. same_mobile      int           1=match, 0=both present but differ, -1=either null
  4. dob_match        int           1=exact, 0=differ, -1=either null
  5. village_match    int           1=same village_code, 0=differ, -1=either null
  6. survey_match     int           1=same survey_no, 0=differ, -1=either null
  7. bank_last4_match int           1=same last-4 digits, 0=differ, -1=either null
  8. phonetic_match   int           1=same name_phonetic, 0=differ, -1=either null

Pure Python — no DB access.
"""

from __future__ import annotations

import jellyfish

from app.resolution.blocking import Record


def build_feature_vector(a: Record, b: Record) -> dict[str, float | int]:
    """
    Compute the 8-dimensional feature vector for the candidate pair (a, b).

    Sentinal value -1 is used for any feature where one or both sides have
    no data, so the ML model can learn to treat missing data differently
    from a genuine mismatch (0).
    """
    return {
        "name_jw": _jw(a.name_norm, b.name_norm),
        "father_name_sim": _jw_nullable(a.father_norm, b.father_norm),
        "same_mobile": _exact_nullable(a.mobile10, b.mobile10),
        "dob_match": _exact_nullable(a.dob, b.dob),
        "village_match": _exact_nullable(a.village_code, b.village_code),
        "survey_match": _exact_nullable(a.survey_no, b.survey_no),
        "bank_last4_match": _exact_nullable(a.bank_last4, b.bank_last4),
        "phonetic_match": _exact_nullable(a.name_phonetic, b.name_phonetic),
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _jw(s1: str | None, s2: str | None) -> float:
    """
    Jaro-Winkler similarity in [0, 1].
    Returns 0.0 if either string is missing (treat as complete mismatch for names).
    """
    if not s1 or not s2:
        return 0.0
    return jellyfish.jaro_winkler_similarity(s1, s2)


def _jw_nullable(s1: str | None, s2: str | None) -> float:
    """
    Jaro-Winkler similarity, but returns -1.0 when either value is missing.
    Used for optional fields like father_name.
    """
    if not s1 or not s2:
        return -1.0
    return jellyfish.jaro_winkler_similarity(s1, s2)


def _exact_nullable(v1: str | None, v2: str | None) -> int:
    """
    Exact categorical comparison:
      1  → both present and equal
      0  → both present but different
     -1  → either is missing / null
    """
    if not v1 or not v2:
        return -1
    return 1 if v1 == v2 else 0
