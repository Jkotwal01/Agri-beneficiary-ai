"""Rule 5: Farmer enrolled in mutually exclusive schemes simultaneously."""

from __future__ import annotations

from app.duplicates.base import DuplicateRule, FlagData

# Pairs of scheme names that cannot be held at the same time
EXCLUSIVE_PAIRS: list[tuple[str, str]] = [
    ("PM_KISAN", "PMKISAN"),  # duplicate names for same scheme
]


class MutuallyExclusive(DuplicateRule):
    def check(self, farmer_id: int, facts: dict) -> list[FlagData]:
        scheme_names: list[str] = [
            (e.get("scheme_name") or "").upper() for e in facts.get("enrollments", [])
        ]
        flags: list[FlagData] = []
        for a, b in EXCLUSIVE_PAIRS:
            if a in scheme_names and b in scheme_names:
                flags.append(
                    FlagData(
                        rule="MutuallyExclusive",
                        severity="High",
                        message=f"Farmer {farmer_id} enrolled in mutually exclusive schemes {a} and {b}",
                    )
                )
        return flags
