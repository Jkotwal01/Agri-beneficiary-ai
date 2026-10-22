"""Rule 1: Farmer enrolled in the same scheme twice in the same season."""

from __future__ import annotations

from app.duplicates.base import DuplicateRule, FlagData


class SameSchemeTwice(DuplicateRule):
    def check(self, farmer_id: int, facts: dict) -> list[FlagData]:
        enrollments = facts.get("enrollments", [])
        seen: set[tuple] = set()
        flags: list[FlagData] = []
        for e in enrollments:
            key = (e.get("scheme_id"), e.get("season") or "")
            if key in seen:
                flags.append(
                    FlagData(
                        rule="SameSchemeTwice",
                        severity="High",
                        message=f"Farmer {farmer_id} enrolled in scheme {key[0]} twice in season '{key[1]}'",
                    )
                )
            seen.add(key)
        return flags
