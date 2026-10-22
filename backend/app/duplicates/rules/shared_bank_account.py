"""Rule 3: Two different farmers share the same bank account (last 4 digits + IFSC)."""

from __future__ import annotations

from app.duplicates.base import DuplicateRule, FlagData


class SharedBankAccount(DuplicateRule):
    def check(self, farmer_id: int, facts: dict) -> list[FlagData]:
        shared = facts.get("shared_bank_farmer_ids", [])
        if shared:
            return [
                FlagData(
                    rule="SharedBankAccount",
                    severity="High",
                    message=(
                        f"Farmer {farmer_id} shares bank account with farmer IDs: {shared}"
                    ),
                )
            ]
        return []
