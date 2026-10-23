"""
Evaluation — Spec Section 15, resolution quality metrics.

evaluate_resolution(db) compares each scored MatchCandidate's decision
against ground_truth.csv (true_farmer_id per source row) and reports
precision / recall / F1 at the candidate-pair level, plus the
auto_link_rate and review_rate across all scored pairs.

Ground truth is keyed by (source_name, source_row_id) -> true_farmer_id,
same join keys as source_records. A pair counts as a "true match" only
when BOTH sides are present in the ground truth and share the same
true_farmer_id; pairs where either side is unlabeled are excluded from
precision/recall (their truth is unknown), but still count toward
auto_link_rate / review_rate.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.clean_record import CleanRecord
from app.models.match_candidate import MatchCandidate
from app.models.source_record import SourceRecord

GROUND_TRUTH_SAMPLE_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "data"
    / "synthetic"
    / "samples"
    / "ground_truth.csv"
)

_LINKED_DECISIONS = {"auto_link", "manual_link"}


@dataclass
class EvaluationMetrics:
    precision: float
    recall: float
    f1: float
    auto_link_rate: float
    review_rate: float


def load_ground_truth(
    path: Path = GROUND_TRUTH_SAMPLE_PATH,
) -> dict[tuple[str, str], str]:
    """Return {(source, source_row_pk): true_farmer_id} from ground_truth.csv."""
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {
            (row["source"], row["source_row_pk"]): row["true_farmer_id"]
            for row in reader
        }


def _clean_record_truth_map(db: Session) -> dict[int, str]:
    """Map clean_record.id -> true_farmer_id, for clean_records traceable to ground truth."""
    ground_truth = load_ground_truth()
    if not ground_truth:
        return {}

    src_lookup = {
        sr.id: (sr.source_name, sr.source_row_id) for sr in db.query(SourceRecord).all()
    }
    result: dict[int, str] = {}
    for clean in db.query(CleanRecord).all():
        key = src_lookup.get(clean.source_record_id)
        if key is None:
            continue
        true_id = ground_truth.get(key)
        if true_id is not None:
            result[clean.id] = true_id
    return result


def evaluate_resolution(db: Session) -> EvaluationMetrics:
    candidates = db.query(MatchCandidate).all()
    total = len(candidates)
    if total == 0:
        return EvaluationMetrics(
            precision=0.0, recall=0.0, f1=0.0, auto_link_rate=0.0, review_rate=0.0
        )

    auto_link_count = sum(1 for c in candidates if c.decision in _LINKED_DECISIONS)
    review_count = sum(1 for c in candidates if c.decision == "review")
    auto_link_rate = auto_link_count / total
    review_rate = review_count / total

    truth_map = _clean_record_truth_map(db)
    tp = fp = fn = 0
    for c in candidates:
        true_a = truth_map.get(c.record_a)
        true_b = truth_map.get(c.record_b)
        if true_a is None or true_b is None:
            continue  # truth unknown for this pair — excluded from precision/recall

        is_true_match = true_a == true_b
        is_predicted_match = c.decision in _LINKED_DECISIONS

        if is_predicted_match and is_true_match:
            tp += 1
        elif is_predicted_match and not is_true_match:
            fp += 1
        elif not is_predicted_match and is_true_match:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return EvaluationMetrics(
        precision=precision,
        recall=recall,
        f1=f1,
        auto_link_rate=auto_link_rate,
        review_rate=review_rate,
    )
