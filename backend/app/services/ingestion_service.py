"""IngestionService — orchestrates reading CSVs and writing source_records."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.ingestion.registry import ADAPTER_REGISTRY, SOURCE_FILES
from app.models.source_record import SourceRecord
from app.repositories.base import BaseRepository


class IngestionService:
    """Reads every source CSV and inserts rows into source_records.

    Constructor injection keeps this class DB-agnostic in tests.
    """

    def __init__(self, db: Session) -> None:
        self._repo: BaseRepository[SourceRecord] = BaseRepository(SourceRecord, db)

    def ingest_all(self, data_dir: Path) -> dict[str, int]:
        """Ingest all known sources. Returns {source_name: rows_inserted}."""
        results: dict[str, int] = {}
        for source_name, filename in SOURCE_FILES.items():
            filepath = data_dir / filename
            if not filepath.exists():
                results[source_name] = 0
                continue
            count = self._ingest_one(source_name, filepath)
            results[source_name] = count
        return results

    def _ingest_one(self, source_name: str, filepath: Path) -> int:
        adapter = ADAPTER_REGISTRY[source_name]()
        count = 0
        for common_dict in adapter.read(filepath):
            record = SourceRecord(
                source_name=source_name,
                source_row_id=str(
                    common_dict.get("agristack_id")
                    or common_dict.get("beneficiary_no")
                    or common_dict.get("policy_no")
                    or common_dict.get("app_id")
                    or common_dict.get("card_no")
                    or f"{source_name}_{count}"
                ),
                raw_json=common_dict,
            )
            self._repo.save(record)
            count += 1
        return count
