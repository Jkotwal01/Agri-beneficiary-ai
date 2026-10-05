"""
Blocking — Spec Section 6, Module 3, Stage 1.

PhoneticVillageBlocker generates candidate pairs using THREE blocking keys:
  Key 1: district_code + name_phonetic     (same district, phonetically similar name)
  Key 2: mobile10                          (exact mobile match)
  Key 3: village_code + survey_no          (same village and land parcel)

Only pairs produced by at least one key are returned.
Pure Python — no DB access.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any


@dataclass
class Record:
    """
    Minimal DTO that the blocker works with.
    Matches the columns present in clean_records.
    """

    id: int
    name_norm: str | None = None
    father_norm: str | None = None
    name_phonetic: str | None = None
    mobile10: str | None = None
    village_code: str | None = None
    district_code: str | None = None
    survey_no: str | None = None
    dob: str | None = None
    bank_last4: str | None = None
    crop: str | None = None
    season: str | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Record:
        return cls(
            id=d["id"],
            name_norm=d.get("name_norm"),
            father_norm=d.get("father_norm"),
            name_phonetic=d.get("name_phonetic"),
            mobile10=d.get("mobile10"),
            village_code=d.get("village_code"),
            district_code=d.get("district_code"),
            survey_no=d.get("survey_no"),
            dob=d.get("dob"),
            bank_last4=d.get("bank_last4"),
            crop=d.get("crop"),
            season=d.get("season"),
        )


class PhoneticVillageBlocker:
    """
    Generates candidate (id_a, id_b) pairs using three blocking keys.

    Usage::
        blocker = PhoneticVillageBlocker()
        pairs = blocker.candidate_pairs(records)   # list of sorted (int, int) tuples
    """

    # ------------------------------------------------------------------
    def candidate_pairs(self, records: list[Record]) -> list[tuple[int, int]]:
        """
        Return deduplicated, sorted candidate pairs from all three blocking keys.
        Pairs are always (min_id, max_id) so duplicates collapse cleanly.
        """
        seen: set[tuple[int, int]] = set()

        for pair in self._key1_district_phonetic(records):
            seen.add(pair)
        for pair in self._key2_mobile(records):
            seen.add(pair)
        for pair in self._key3_village_survey(records):
            seen.add(pair)

        return list(seen)

    # ------------------------------------------------------------------
    # Private helpers — one per blocking key
    # ------------------------------------------------------------------
    @staticmethod
    def _key1_district_phonetic(records: list[Record]) -> list[tuple[int, int]]:
        """Key 1: district_code + name_phonetic."""
        buckets: dict[str, list[int]] = defaultdict(list)
        for r in records:
            if r.district_code and r.name_phonetic:
                buckets[f"{r.district_code}|{r.name_phonetic}"].append(r.id)
        return _pairs_from_buckets(buckets)

    @staticmethod
    def _key2_mobile(records: list[Record]) -> list[tuple[int, int]]:
        """Key 2: mobile10 (exact 10-digit match)."""
        buckets: dict[str, list[int]] = defaultdict(list)
        for r in records:
            if r.mobile10:
                buckets[r.mobile10].append(r.id)
        return _pairs_from_buckets(buckets)

    @staticmethod
    def _key3_village_survey(records: list[Record]) -> list[tuple[int, int]]:
        """Key 3: village_code + survey_no."""
        buckets: dict[str, list[int]] = defaultdict(list)
        for r in records:
            if r.village_code and r.survey_no:
                buckets[f"{r.village_code}|{r.survey_no}"].append(r.id)
        return _pairs_from_buckets(buckets)


# ------------------------------------------------------------------
# Utility
# ------------------------------------------------------------------
def _pairs_from_buckets(buckets: dict[str, list[int]]) -> list[tuple[int, int]]:
    """
    Enumerate all (a, b) pairs within each bucket where a < b.
    O(B * k^2) where B = buckets, k = average bucket size.
    """
    pairs: list[tuple[int, int]] = []
    for ids in buckets.values():
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = ids[i], ids[j]
                pairs.append((a, b) if a < b else (b, a))
    return pairs
