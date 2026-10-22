"""Rule 2: Farmer claims land area exceeding actual parcel area."""

from __future__ import annotations

from app.duplicates.base import DuplicateRule, FlagData


class ParcelOverclaim(DuplicateRule):
    def check(self, farmer_id: int, facts: dict) -> list[FlagData]:
        total_land = facts.get("total_land_ha") or 0.0
        claimed = facts.get("claimed_area_ha") or 0.0
        if claimed > total_land > 0:
            return [
                FlagData(
                    rule="ParcelOverclaim",
                    severity="Medium",
                    message=(
                        f"Farmer {farmer_id} claims {claimed:.2f} ha but owns {total_land:.2f} ha"
                    ),
                )
            ]
        return []
