"""
Explainability — Spec Section 6, Module 3, Stage 3 (SHAP-style feature attribution).

top_shap_features(pair_features) ranks each pair-feature's contribution toward
the match score, using the same relative weights as the matcher's fallback
heuristic (app.resolution.matcher._heuristic_score). A feature with value -1
(missing/not comparable) contributes nothing.
"""

from __future__ import annotations

from dataclasses import dataclass

_WEIGHTS: dict[str, float] = {
    "name_jw": 0.30,
    "father_name_sim": 0.15,
    "same_mobile": 0.20,
    "dob_match": 0.10,
    "village_match": 0.05,
    "survey_match": 0.05,
    "bank_last4_match": 0.10,
    "phonetic_match": 0.05,
}

MAX_FEATURES = 4

# Continuous similarity features — the raw value IS the signed contribution
# magnitude. Everything else is categorical (1 / 0 / -1 sentinel).
_CONTINUOUS_FEATURES = {"name_jw", "father_name_sim"}


@dataclass
class ShapFeature:
    feature: str
    value: str
    shap_value: float


def top_shap_features(
    pair_features: dict, limit: int = MAX_FEATURES
) -> list[ShapFeature]:
    """Return up to `limit` pair-features ranked by |contribution|, highest first."""
    contributions: list[ShapFeature] = []
    for feature, weight in _WEIGHTS.items():
        if feature not in pair_features:
            continue
        value = pair_features[feature]
        if value == -1:
            continue  # not comparable — excluded, matching matcher's heuristic

        if feature in _CONTINUOUS_FEATURES:
            signed = (value * 2) - 1  # map [0,1] similarity to [-1,1] contribution
        else:
            signed = 1.0 if value == 1 else -1.0

        contributions.append(
            ShapFeature(
                feature=feature, value=str(value), shap_value=round(weight * signed, 4)
            )
        )

    contributions.sort(key=lambda sf: abs(sf.shap_value), reverse=True)
    return contributions[:limit]
