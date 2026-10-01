"""PMFBY (crop insurance) adapter."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pandas as pd

from app.ingestion.base import SourceAdapter

COLUMN_MAP = {
    "policy_no": "policy_no",
    "name": "name",
    "village": "village_code",
    "survey_no": "survey_no",
    "crop": "crop",
    "season": "season",
    "area_ha": "land_ha",
    "bank_acct_last4": "bank_last4",
}


class PmfbyAdapter(SourceAdapter):
    source_name = "pmfby"

    def read(self, path: Path) -> Iterable[dict]:
        df = pd.read_csv(path, dtype=str).fillna("")
        for row in df.to_dict("records"):
            yield {new: row.get(old, "") for old, new in COLUMN_MAP.items()}
