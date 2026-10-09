"""
Golden Record Survivorship — Spec Section 6, Module 3, Stage 5.

TrustOrderGoldenRecordBuilder selects the best field value from a cluster
of clean_records based on a source trust hierarchy:
  AgriStack > PM-KISAN > PMFBY > NFSM > KCC > (others)

For each field, the value from the highest-trust source that is non-null wins.
"""

from __future__ import annotations

from typing import ClassVar

from app.resolution.blocking import Record

# Source trust order: index 0 = highest trust
TRUST_ORDER = ["agristack", "pm_kisan", "pmkisan", "pmfby", "nfsm", "kcc"]


def _source_rank(source: str | None) -> int:
    """Lower rank = higher trust."""
    if not source:
        return len(TRUST_ORDER)
    s = source.lower().replace("-", "_").replace(" ", "_")
    for i, t in enumerate(TRUST_ORDER):
        if s.startswith(t):
            return i
    return len(TRUST_ORDER)


class TrustOrderGoldenRecordBuilder:
    """
    Builds a golden record dict from a cluster of (Record, source_name) pairs.
    For each field, pick the value from the highest-trust source that is non-null.
    """

    FIELDS: ClassVar[list[str]] = [
        "name_norm",
        "father_norm",
        "name_phonetic",
        "mobile10",
        "village_code",
        "district_code",
        "survey_no",
        "dob",
        "bank_last4",
        "crop",
        "season",
    ]

    def build(
        self,
        records: list[tuple[Record, str]],  # (record, source_name)
        confidence: float = 1.0,
    ) -> dict:
        """
        Args:
            records:    List of (Record, source_name) for the cluster.
            confidence: Match confidence score from the matcher.

        Returns:
            Dict with best field values and metadata.
        """
        # Sort by trust rank (ascending = highest trust first)
        sorted_records = sorted(records, key=lambda x: _source_rank(x[1]))

        golden: dict = {}
        for field in self.FIELDS:
            for rec, _ in sorted_records:
                val = getattr(rec, field, None)
                if val:
                    golden[field] = val
                    break
            else:
                golden[field] = None

        golden["confidence"] = confidence
        golden["source_count"] = len(records)
        golden["source_ids"] = [r.id for r, _ in records]
        return golden
