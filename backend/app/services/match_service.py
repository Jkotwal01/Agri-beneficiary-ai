"""MatchService — review-queue listing and manual link/reject decisions."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.clean_record import CleanRecord
from app.models.match_candidate import MatchCandidate
from app.models.source_record import SourceRecord
from app.resolution.explainability import top_shap_features

_DECISION_MAP = {
    "confirm": "manual_link",
    "reject": "no_match",
}


class MatchService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_matches(self, decision: str | None = None) -> list[dict]:
        db = self._db
        q = db.query(MatchCandidate)
        if decision:
            q = q.filter(MatchCandidate.decision == decision)
        rows = q.order_by(MatchCandidate.id).all()
        return [self._to_dict(row) for row in rows]

    def decide(self, match_id: int, decision_in: str, reviewer_id: int) -> dict:
        if decision_in not in _DECISION_MAP:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="decision must be 'confirm' or 'reject'",
            )

        match = self._db.get(MatchCandidate, match_id)
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
            )

        match.decision = _DECISION_MAP[decision_in]
        match.reviewed_by = reviewer_id
        match.reviewed_at = datetime.now(UTC)

        self._db.add(
            AuditLog(
                user_id=reviewer_id,
                action=f"match_decision→{match.decision}",
                entity="match_candidates",
                entity_id=match_id,
            )
        )
        self._db.commit()
        self._db.refresh(match)
        return self._to_dict(match)

    def _clean_record_out(self, clean_record_id: int) -> dict | None:
        record = self._db.get(CleanRecord, clean_record_id)
        if record is None:
            return None
        source = self._db.get(SourceRecord, record.source_record_id)
        return {
            "id": record.id,
            "source_name": source.source_name if source else None,
            "name_norm": record.name_norm,
            "mobile10": record.mobile10,
            "district_code": record.district_code,
            "village_code": record.village_code,
            "survey_no": record.survey_no,
            "dob": record.dob,
        }

    def _to_dict(self, match: MatchCandidate) -> dict:
        features = match.features_json or {}
        return {
            "id": match.id,
            "score": match.score,
            "decision": match.decision,
            "record_a": self._clean_record_out(match.record_a),
            "record_b": self._clean_record_out(match.record_b),
            "features": features,
            "shap": top_shap_features(features),
            "reviewed_by": match.reviewed_by,
            "reviewed_at": match.reviewed_at,
        }
