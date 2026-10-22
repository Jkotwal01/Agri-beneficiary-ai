"""
Profile Linker — Spec Section 16, links a self-registered farmer profile to
an existing golden-record Farmer, reusing the same name-similarity approach
as the Phase 6 blocking/matching pipeline (jellyfish Jaro-Winkler).

link(db, profile) -> (farmer_id | None, method, score)
  method="rule"  — exact mobile match -> linked with score 1.0
  method="score" — best Jaro-Winkler name match >= LINK_THRESHOLD -> linked
  method="none"  — best score < CREATE_THRESHOLD -> no link, caller creates
                    a new Farmer row
"""

from __future__ import annotations

import jellyfish
from sqlalchemy.orm import Session

from app.models.farmer import Farmer
from app.models.farmer_profile import FarmerProfile

LINK_THRESHOLD = 0.90
CREATE_THRESHOLD = 0.60


def link(db: Session, profile: FarmerProfile) -> tuple[int | None, str, float]:
    """Attempt to link `profile` to an existing Farmer golden record."""
    if profile.mobile:
        exact = db.query(Farmer).filter(Farmer.mobile == profile.mobile).first()
        if exact is not None:
            return exact.id, "rule", 1.0

    if not profile.full_name:
        return None, "none", 0.0

    best_farmer: Farmer | None = None
    best_score = 0.0
    for farmer in db.query(Farmer).all():
        if not farmer.name:
            continue
        s = jellyfish.jaro_winkler_similarity(
            profile.full_name.lower(), farmer.name.lower()
        )
        if s > best_score:
            best_score = s
            best_farmer = farmer

    if best_farmer is not None and best_score >= LINK_THRESHOLD:
        return best_farmer.id, "score", best_score
    if best_farmer is not None and best_score >= CREATE_THRESHOLD:
        return None, "none", best_score

    return None, "none", best_score
