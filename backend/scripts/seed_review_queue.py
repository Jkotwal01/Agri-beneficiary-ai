"""
Seed realistic borderline match candidates into the Officer Review Queue.
Sets 15 candidate pairs with uncertainty band scores [0.60 - 0.80] to decision='review'
so the officer can review, compare, and merge/reject them.
"""

from __future__ import annotations

import random

from sqlalchemy import Float, cast

from app.core.db import SessionLocal
from app.models.match_candidate import MatchCandidate


def seed_review_queue():
    db = SessionLocal()
    try:
        # Find 15 candidates with high fuzzy name similarity that are currently no_match or auto_link
        candidates = (
            db.query(MatchCandidate)
            .filter(
                cast(MatchCandidate.features_json["name_jw"].astext, Float) >= 0.75,
                cast(MatchCandidate.features_json["name_jw"].astext, Float) <= 0.96,
            )
            .limit(15)
            .all()
        )

        if not candidates:
            print("No matching candidate pairs found to put in review.")
            return

        for idx, c in enumerate(candidates):
            c.decision = "review"
            c.reviewed_by = None
            c.reviewed_at = None
            # Set confidence score in uncertainty band [0.61 - 0.79]
            c.score = round(random.uniform(0.63, 0.79), 3)

        db.commit()
        print(
            f"Successfully placed {len(candidates)} borderline candidate pairs into the Review Queue!"
        )

    except Exception as e:
        db.rollback()
        print(f"Error seeding review queue: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_review_queue()
