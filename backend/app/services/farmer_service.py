"""FarmerService — builds the Farmer 360 detail payload."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.clean_record import CleanRecord
from app.models.enrollment import Enrollment
from app.models.farmer import Farmer
from app.models.farmer_link import FarmerLink
from app.models.flag import Flag
from app.models.recommendation import Recommendation
from app.models.scheme import Scheme
from app.models.source_record import SourceRecord


class FarmerService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_detail(self, farmer_id: int) -> dict:
        db = self._db
        farmer = db.get(Farmer, farmer_id)
        if not farmer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Farmer not found"
            )

        links = db.query(FarmerLink).filter(FarmerLink.farmer_id == farmer_id).all()
        linked_records = []
        for link in links:
            clean = db.get(CleanRecord, link.clean_record_id)
            source_name = None
            if clean is not None:
                source = db.get(SourceRecord, clean.source_record_id)
                source_name = source.source_name if source else None
            linked_records.append(
                {
                    "id": link.id,
                    "method": link.method,
                    "score": link.score,
                    "source_name": source_name,
                }
            )

        schemes_by_id = {s.id: s.code for s in db.query(Scheme).all()}

        enrollments = [
            {
                "id": e.id,
                "scheme_id": e.scheme_id,
                "scheme_code": schemes_by_id.get(e.scheme_id),
                "season": e.season,
                "amount": e.amount,
            }
            for e in db.query(Enrollment)
            .filter(Enrollment.farmer_id == farmer_id)
            .all()
        ]

        flags = [
            {
                "id": f.id,
                "type": f.type,
                "severity": f.severity,
                "reason": f.reason,
                "status": f.status,
            }
            for f in db.query(Flag).filter(Flag.farmer_id == farmer_id).all()
        ]

        recommendations = [
            {
                "id": r.id,
                "scheme_id": r.scheme_id,
                "scheme_code": schemes_by_id.get(r.scheme_id),
                "eligible": r.eligible,
                "already_enrolled": r.already_enrolled,
                "reasons": r.reasons_json or [],
            }
            for r in db.query(Recommendation)
            .filter(Recommendation.farmer_id == farmer_id)
            .all()
        ]

        return {
            "id": farmer.id,
            "name": farmer.name,
            "father_name": farmer.father_name,
            "dob": farmer.dob,
            "mobile": farmer.mobile,
            "village_code": farmer.village_code,
            "district_code": farmer.district_code,
            "total_land_ha": farmer.total_land_ha,
            "category": farmer.category,
            "confidence": farmer.confidence,
            "linked_records": linked_records,
            "enrollments": enrollments,
            "flags": flags,
            "recommendations": recommendations,
        }
