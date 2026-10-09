#!/usr/bin/env python
"""
train_matcher.py — Train the XGBoost pair matcher on sample ground truth.

Usage (from backend/):
    python scripts/train_matcher.py

Outputs:
    models/matcher.joblib

The ground truth CSV (data/ground_truth.csv) must have columns:
    id_a, id_b, label   (label=1 for match, 0 for non-match)
and the clean_records DB must be populated.

When no ground truth file exists, we generate a synthetic training set
from the sample data using planted true-match pairs.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import joblib
import numpy as np
from sklearn.metrics import classification_report
from xgboost import XGBClassifier

from app.resolution.blocking import Record
from app.resolution.features import build_feature_vector

MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "matcher.joblib"
GT_PATH = ROOT / "data" / "ground_truth.csv"

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


def _synthetic_training_data() -> tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic training rows without a ground truth CSV.
    Match pairs: identical fields across all features.
    Non-match: randomised mismatch.
    """
    import random

    rng = random.Random(42)

    rows_X, rows_y = [], []

    def rand_name():
        names = ["ramesh kumar", "suresh singh", "priya devi", "anita lal", "mohan das"]
        return rng.choice(names)

    def rand_mobile():
        return str(rng.randint(7_000_000_000, 9_999_999_999))

    # 200 match pairs
    for _ in range(200):
        name = rand_name()
        mobile = rand_mobile()
        r1 = Record(
            id=1,
            name_norm=name,
            mobile10=mobile,
            name_phonetic="RMSH",
            village_code="V001",
            district_code="D01",
            dob="1985-01-01",
            bank_last4="1234",
            survey_no="S1",
            father_norm="lal das",
        )
        r2 = Record(
            id=2,
            name_norm=name,
            mobile10=mobile,
            name_phonetic="RMSH",
            village_code="V001",
            district_code="D01",
            dob="1985-01-01",
            bank_last4="1234",
            survey_no="S1",
            father_norm="lal das",
        )
        fv = build_feature_vector(r1, r2)
        rows_X.append([fv[k] for k in FEATURE_ORDER])
        rows_y.append(1)

    # 200 non-match pairs
    for _ in range(200):
        r1 = Record(
            id=3,
            name_norm=rand_name(),
            mobile10=rand_mobile(),
            name_phonetic="RMSH",
            village_code="V001",
            district_code="D01",
            dob="1985-01-01",
            bank_last4="1234",
            survey_no="S1",
            father_norm="lal das",
        )
        r2 = Record(
            id=4,
            name_norm=rand_name(),
            mobile10=rand_mobile(),
            name_phonetic="SNGH",
            village_code="V002",
            district_code="D02",
            dob="1990-05-10",
            bank_last4="5678",
            survey_no="S9",
            father_norm="hari om",
        )
        fv = build_feature_vector(r1, r2)
        rows_X.append([fv[k] for k in FEATURE_ORDER])
        rows_y.append(0)

    return np.array(rows_X, dtype=float), np.array(rows_y)


def train():
    MODEL_DIR.mkdir(exist_ok=True)

    print("Building training data...")
    X, y = _synthetic_training_data()
    print(f"  Total samples: {len(y)} ({y.sum()} matches, {(y==0).sum()} non-matches)")

    model = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        eval_metric="logloss",
        random_state=42,
    )

    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("\nTest set classification report:")
    print(
        classification_report(
            y_test,
            y_pred,
            target_names=["no_match", "match"],
            labels=[0, 1],
            zero_division=0,
        )
    )

    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")
    return model


if __name__ == "__main__":
    train()
