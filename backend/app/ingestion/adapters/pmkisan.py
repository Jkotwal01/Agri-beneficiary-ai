"""PM-KISAN adapter."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pandas as pd

from app.ingestion.base import SourceAdapter

COLUMN_MAP = {
    "beneficiary_no": "beneficiary_no",
    "name": "name",
    "father_name": "father_name",
    "mobile": "mobile",
    "bank_acct_last4": "bank_last4",
    "village": "village_code",
    "district": "district_code",
    "land_ha": "land_ha",
}


class PmKisanAdapter(SourceAdapter):
    source_name = "pmkisan"

    def read(self, path: Path) -> Iterable[dict]:
        df = pd.read_csv(path, dtype=str).fillna("")
        for row in df.to_dict("records"):
            yield {new: row.get(old, "") for old, new in COLUMN_MAP.items()}
