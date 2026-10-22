"""ReportService — aggregation queries for dashboard KPIs, coverage and exports."""
from __future__ import annotations

import csv
import io

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.farmer import Farmer
from app.models.flag import Flag
from app.models.recommendation import Recommendation
from app.models.scheme import Scheme
from app.models.source_record import SourceRecord


class ReportService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def summary(self) -> dict:
        db = self._db
        total_records = db.query(func.count(SourceRecord.id)).scalar() or 0
        unique_farmers = db.query(func.count(Farmer.id)).scalar() or 0
        open_flags = (
            db.query(func.count(Flag.id)).filter(Flag.status == "open").scalar() or 0
        )
        exclusions = self._exclusions_query().count()
        return {
            "total_records": total_records,
            "unique_farmers": unique_farmers,
            "open_flags": open_flags,
            "exclusions": exclusions,
        }

    def coverage(self, group_by: str = "district") -> list[dict]:
        db = self._db
        group_col = Farmer.district_code if group_by == "district" else Farmer.village_code

        groups = (
            db.query(group_col.label("group"), func.count(Farmer.id).label("count"))
            .filter(group_col.isnot(None))
            .group_by(group_col)
            .all()
        )

        result = []
        for group_value, count in groups:
            scheme_rows = (
                db.query(Scheme.code, func.count(Recommendation.id))
                .join(Recommendation, Recommendation.scheme_id == Scheme.id)
                .join(Farmer, Farmer.id == Recommendation.farmer_id)
                .filter(group_col == group_value, Recommendation.already_enrolled.is_(True))
                .group_by(Scheme.code)
                .all()
            )
            result.append({
                "group": group_value,
                "count": count,
                "scheme_coverage": [
                    {"scheme_code": code, "enrolled_count": enrolled_count}
                    for code, enrolled_count in scheme_rows
                ],
            })
        return result

    def _exclusions_query(self):
        return self._db.query(Recommendation).filter(
            Recommendation.eligible.is_(True),
            Recommendation.already_enrolled.is_(False),
        )

    def exclusions(
        self, district: str | None = None, scheme: str | None = None
    ) -> list[dict]:
        q = (
            self._exclusions_query()
            .join(Farmer, Farmer.id == Recommendation.farmer_id)
            .join(Scheme, Scheme.id == Recommendation.scheme_id)
        )
        if district:
            q = q.filter(Farmer.district_code == district)
        if scheme:
            q = q.filter(Scheme.code == scheme)

        rows = q.with_entities(
            Farmer.id, Farmer.name, Farmer.district_code, Farmer.village_code,
            Scheme.code, Recommendation.reasons_json,
        ).all()

        return [
            {
                "farmer_id": farmer_id,
                "farmer_name": name,
                "district_code": district_code,
                "village_code": village_code,
                "scheme_code": scheme_code,
                "reasons": reasons_json or [],
            }
            for farmer_id, name, district_code, village_code, scheme_code, reasons_json in rows
        ]

    def export_csv(self, type_: str) -> str:
        if type_ != "exclusions":
            raise ValueError(f"Unsupported export type: {type_}")

        rows = self.exclusions()
        buffer = io.StringIO()
        writer = csv.DictWriter(
            buffer,
            fieldnames=["farmer_id", "farmer_name", "district_code", "village_code", "scheme_code"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in writer.fieldnames})
        return buffer.getvalue()
