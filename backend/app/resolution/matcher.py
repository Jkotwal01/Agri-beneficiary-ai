"""
ML Matcher — Spec Section 6, Module 3, Stage 3.

XGBoostPairMatcher:   loads a trained XGBoost model and returns P(match) in [0,1].
RuleShortcutMatcher:  deterministic shortcut rules applied BEFORE the ML model.
                      - If mobile10 match + phonetic match → instant LINK (score=1.0)
                      - If all 5 categorical features are 0 (all mismatch) → instant NO_MATCH (score=0.0)

Thresholds (spec defaults):
  score ≥ 0.80  → "auto_link"
  0.50 ≤ score < 0.80 → "review"
  score < 0.50  → "no_match"
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import joblib
import numpy as np

from app.resolution.blocking import Record
from app.resolution.features import build_feature_vector

MODEL_PATH = Path(os.getenv("MATCHER_MODEL_PATH", "models/matcher.joblib"))

FEATURE_ORDER = [
    "name_jw",
    "father_name_sim",
    "same_mobile",
    "dob_match",
    "village_match",
    "survey_match",
    "bank_last4_match",
    "phonetic_match",
]

Decision = Literal["auto_link", "review", "no_match"]

THRESHOLD_LINK = 0.80
THRESHOLD_REVIEW = 0.50


def _decision(score: float) -> Decision:
    if score >= THRESHOLD_LINK:
        return "auto_link"
    if score >= THRESHOLD_REVIEW:
        return "review"
    return "no_match"


class RuleShortcutMatcher:
    """
    Fast deterministic shortcuts applied before the ML model.
    Returns (score, decision) or None if no shortcut applies.
    """

    @staticmethod
    def evaluate(fv: dict) -> tuple[float, Decision] | None:
        # Definite LINK: mobile match AND phonetic match
        if fv.get("same_mobile") == 1 and fv.get("phonetic_match") == 1:
            return 1.0, "auto_link"
        # Definite NO_MATCH: all 5 categorical features are mismatch (0)
        categoricals = [
            "same_mobile",
            "dob_match",
            "village_match",
            "survey_match",
            "bank_last4_match",
        ]
        if all(fv.get(k) == 0 for k in categoricals):
            return 0.0, "no_match"
        return None


class XGBoostPairMatcher:
    """
    XGBoost-based pair scorer.
    Loads model lazily on first call.
    Falls back to a heuristic score if no model file exists.
    """

    def __init__(self, model_path: Path = MODEL_PATH) -> None:
        self._model_path = model_path
        self._model = None

    def _load(self):
        if self._model is None and self._model_path.exists():
            self._model = joblib.load(self._model_path)

    def score(self, a: Record, b: Record) -> float:
        """Return P(match) in [0, 1]."""
        fv = build_feature_vector(a, b)

        # Try rule shortcut first
        shortcut = RuleShortcutMatcher.evaluate(fv)
        if shortcut is not None:
            return shortcut[0]

        self._load()
        if self._model is not None:
            X = np.array([[fv[k] for k in FEATURE_ORDER]], dtype=float)
            return float(self._model.predict_proba(X)[0, 1])

        # Fallback heuristic when no model is trained yet
        return _heuristic_score(fv)

    def score_with_decision(self, a: Record, b: Record) -> tuple[float, dict, Decision]:
        """Return (score, feature_vector, decision)."""
        fv = build_feature_vector(a, b)
        shortcut = RuleShortcutMatcher.evaluate(fv)
        if shortcut is not None:
            return shortcut[0], fv, shortcut[1]

        self._load()
        if self._model is not None:
            X = np.array([[fv[k] for k in FEATURE_ORDER]], dtype=float)
            sc = float(self._model.predict_proba(X)[0, 1])
        else:
            sc = _heuristic_score(fv)

        return sc, fv, _decision(sc)


def _heuristic_score(fv: dict) -> float:
    """
    Weighted heuristic used when no trained model exists.
    Weights approximate the relative importance of each feature.
    """
    weights = {
        "name_jw": 0.30,
        "father_name_sim": 0.15,
        "same_mobile": 0.20,
        "dob_match": 0.10,
        "village_match": 0.05,
        "survey_match": 0.05,
        "bank_last4_match": 0.10,
        "phonetic_match": 0.05,
    }
    total = 0.0
    norm = 0.0
    for k, w in weights.items():
        v = fv.get(k, -1)
        if v == -1:
            continue  # skip missing
        # Convert -1 sentinel to 0 for heuristic calc
        total += w * max(v, 0.0)
        norm += w
    return total / norm if norm > 0 else 0.0
