"""
PreprocessingPipeline — reads source_records, writes clean_records.

Spec Section 6, Module 2.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.clean_record import CleanRecord
from app.models.source_record import SourceRecord
from app.preprocessing.normalizers import (
    fill_missing,
    normalize_mobile,
    normalize_name,
    parse_dob,
    phonetic_key,
)
from app.repositories.base import BaseRepository


class PreprocessingPipeline:
    """Transforms source_records → clean_records row-by-row."""

    def __init__(self, db: Session) -> None:
        self._src_repo: BaseRepository[SourceRecord] = BaseRepository(SourceRecord, db)
        self._dst_repo: BaseRepository[CleanRecord] = BaseRepository(CleanRecord, db)

    def run(self, batch_size: int = 500) -> int:
        """
        Process all unprocessed source_records → clean_records.
        Returns the number of clean_records written.
        """
        # Get all source_records IDs already processed
        processed_ids = {
            r.source_record_id
            for r in self._dst_repo.get_all()
            if r.source_record_id is not None
        }

        records = self._src_repo.get_all()
        count = 0
        for record in records:
            if record.id in processed_ids:
                continue
            clean = self._transform(record)
            self._dst_repo.save(clean)
            count += 1
        return count

    # ------------------------------------------------------------------
    def _transform(self, record: SourceRecord) -> CleanRecord:
        raw: dict = record.raw_json or {}

        name_raw = raw.get("name", "")
        name_norm = normalize_name(name_raw)
        father_norm = normalize_name(raw.get("father_name", ""))
        mobile10 = normalize_mobile(raw.get("mobile", ""))
        dob = parse_dob(raw.get("dob", ""))

        return CleanRecord(
            source_record_id=record.id,
            name_norm=fill_missing(name_norm),
            father_norm=fill_missing(father_norm),
            name_phonetic=phonetic_key(name_norm),
            mobile10=fill_missing(mobile10),
            village_code=fill_missing(raw.get("village_code") or raw.get("village")),
            district_code=fill_missing(raw.get("district_code") or raw.get("district")),
            survey_no=fill_missing(raw.get("survey_no")),
            dob=dob.isoformat() if dob else None,
            bank_last4=fill_missing(raw.get("bank_last4")),
            land_ha=float(raw["land_ha"]) if raw.get("land_ha") else None,
            crop=fill_missing(raw.get("crop")),
            season=fill_missing(raw.get("season")),
        )
