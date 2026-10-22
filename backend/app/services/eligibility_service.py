"""
EligibilityService — evaluates every farmer against all active schemes
and persists recommendations.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.eligibility.engine import evaluate_all
from app.models.farmer import Farmer
from app.models.recommendation import Recommendation
from app.models.scheme import Scheme


class EligibilityService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def run(self) -> dict:
        db = self._db
        db.query(Recommendation).delete()
        db.flush()

        farmers = db.query(Farmer).all()
        schemes_by_name: dict[str, int] = {
            s.name.upper().replace("-", "_"): s.id
            for s in db.query(Scheme).all()
        }

        recs_created = 0
        for farmer in farmers:
            facts = {
                "total_land_ha": farmer.total_land_ha or 0.0,
                "crop": None,   # enriched later from enrollments
                "category": farmer.category,
            }
            results = evaluate_all(facts)
            for result in results:
                scheme_id = schemes_by_name.get(result.scheme.upper())
                if scheme_id is None:
                    continue
                db.add(Recommendation(
                    farmer_id=farmer.id,
                    scheme_id=scheme_id,
                    eligible=result.eligible,
                    reasons_json=result.reasons,
                    already_enrolled=False,
                    priority=1 if result.eligible else 0,
                ))
                recs_created += 1

        db.commit()
        return {"recommendations_created": recs_created, "farmers_checked": len(farmers)}
