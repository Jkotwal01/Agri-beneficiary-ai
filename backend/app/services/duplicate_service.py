"""
DuplicateService — runs all 5 duplicate rules against every farmer and persists flags.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.duplicates.rules.low_confidence_merge import LowConfidenceMerge
from app.duplicates.rules.mutually_exclusive import MutuallyExclusive
from app.duplicates.rules.parcel_overclaim import ParcelOverclaim
from app.duplicates.rules.same_scheme_twice import SameSchemeTwice
from app.duplicates.rules.shared_bank_account import SharedBankAccount
from app.models.enrollment import Enrollment
from app.models.farmer import Farmer
from app.models.flag import Flag

RULES = [
    SameSchemeTwice(),
    ParcelOverclaim(),
    MutuallyExclusive(),
    LowConfidenceMerge(),
    SharedBankAccount(),
]


class DuplicateService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def run(self) -> dict:
        db = self._db
        # Clear existing flags
        db.query(Flag).delete()
        db.flush()

        farmers = db.query(Farmer).all()
        # Build bank-account sharing map: bank_last4 → [farmer_ids]
        bank_map: dict[str, list[int]] = {}
        for f in farmers:
            mobile = f.mobile or ""
            if len(mobile) >= 4:
                key = mobile[-4:]
                bank_map.setdefault(key, []).append(f.id)

        total_flags = 0
        for farmer in farmers:
            enrollments = db.query(Enrollment).filter(
                Enrollment.farmer_id == farmer.id
            ).all()
            enroll_dicts = [
                {
                    "scheme_id": e.scheme_id,
                    "season": e.season,
                    "scheme_name": str(e.scheme_id),
                }
                for e in enrollments
            ]

            mobile = farmer.mobile or ""
            bank_key = mobile[-4:] if len(mobile) >= 4 else ""
            shared = [
                fid for fid in bank_map.get(bank_key, [])
                if fid != farmer.id
            ]

            facts = {
                "enrollments": enroll_dicts,
                "total_land_ha": farmer.total_land_ha or 0.0,
                "claimed_area_ha": farmer.total_land_ha or 0.0,  # updated later
                "confidence": farmer.confidence,
                "shared_bank_farmer_ids": shared,
            }

            for rule in RULES:
                for fd in rule.check(farmer.id, facts):
                    db.add(Flag(
                        farmer_id=farmer.id,
                        type=fd.rule,
                        severity=fd.severity,
                        reason=fd.message,
                        status="open",
                    ))
                    total_flags += 1

        db.commit()
        return {"flags_created": total_flags, "farmers_checked": len(farmers)}
