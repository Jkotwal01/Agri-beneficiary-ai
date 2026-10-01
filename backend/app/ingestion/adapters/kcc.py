"""KCC (Kisan Credit Card) adapter."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pandas as pd

from app.ingestion.base import SourceAdapter

COLUMN_MAP = {
    "card_no": "card_no",
    "name": "name",
    "dob": "dob",
    "mobile": "mobile",
    "village": "village_code",
    "land_ha": "land_ha",
    "credit_limit": "credit_limit",
}


class KccAdapter(SourceAdapter):
    source_name = "kcc"

    def read(self, path: Path) -> Iterable[dict]:
        df = pd.read_csv(path, dtype=str).fillna("")
        for row in df.to_dict("records"):
            yield {new: row.get(old, "") for old, new in COLUMN_MAP.items()}
