"""AgriStack adapter — maps CSV columns to common field names."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pandas as pd

from app.ingestion.base import SourceAdapter

COLUMN_MAP = {
    "farmer_id": "agristack_id",
    "name": "name",
    "father_name": "father_name",
    "dob": "dob",
    "gender": "gender",
    "mobile": "mobile",
    "village_code": "village_code",
    "district_code": "district_code",
}


class AgriStackAdapter(SourceAdapter):
    source_name = "agristack"

    def read(self, path: Path) -> Iterable[dict]:
        df = pd.read_csv(path, dtype=str).fillna("")
        for row in df.to_dict("records"):
            yield {new: row.get(old, "") for old, new in COLUMN_MAP.items()}
