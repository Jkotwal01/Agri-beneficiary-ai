"""NFSM (seed subsidy) adapter."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pandas as pd

from app.ingestion.base import SourceAdapter

COLUMN_MAP = {
    "app_id": "app_id",
    "name": "name",
    "mobile": "mobile",
    "survey_no": "survey_no",
    "crop": "crop",
    "seed_subsidy_amt": "seed_subsidy_amt",
    "season": "season",
}


class NfsmAdapter(SourceAdapter):
    source_name = "nfsm"

    def read(self, path: Path) -> Iterable[dict]:
        df = pd.read_csv(path, dtype=str).fillna("")
        for row in df.to_dict("records"):
            yield {new: row.get(old, "") for old, new in COLUMN_MAP.items()}
