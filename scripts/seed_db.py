"""
Seed script: reads synthetic CSVs and inserts rows into the source_records table.

Usage (from repo root):
    DATABASE_URL=postgresql+psycopg2://agri:agri@localhost:5432/agri_db \
        PYTHONPATH=backend python scripts/seed_db.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.core.db import SessionLocal
from app.models.source_record import SourceRecord
from app.repositories.base import BaseRepository

DATA_DIR = Path("data/synthetic")

SOURCE_FILES = {
    "agristack": "agristack_farmers.csv",
    "pmkisan": "pmkisan.csv",
    "pmfby": "pmfby.csv",
    "nfsm": "nfsm.csv",
    "kcc": "kcc.csv",
}


def seed(data_dir: Path = DATA_DIR) -> None:
    db = SessionLocal()
    repo: BaseRepository[SourceRecord] = BaseRepository(SourceRecord, db)

    try:
        total = 0
        for source_name, filename in SOURCE_FILES.items():
            filepath = data_dir / filename
            if not filepath.exists():
                print(f"[seed] WARNING: {filepath} not found – skipping.")
                continue

            df = pd.read_csv(filepath)
            pk_col = df.columns[0]

            for _, row in df.iterrows():
                raw = row.dropna().to_dict()
                record = SourceRecord(
                    source_name=source_name,
                    source_row_id=str(raw.get(pk_col, "")),
                    raw_json=raw,
                )
                repo.save(record)
                total += 1

            print(f"[seed] {source_name}: {len(df)} rows inserted.")

        print(f"[seed] Done. Total rows inserted: {total}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
