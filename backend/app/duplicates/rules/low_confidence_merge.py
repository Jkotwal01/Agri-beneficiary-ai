"""Rule 4: Farmer merged with low confidence score (potential wrong merge)."""
from __future__ import annotations

from app.duplicates.base import DuplicateRule, FlagData

LOW_CONFIDENCE_THRESHOLD = 0.70


class LowConfidenceMerge(DuplicateRule):
    def __init__(self, threshold: float = LOW_CONFIDENCE_THRESHOLD) -> None:
        self.threshold = threshold

    def check(self, farmer_id: int, facts: dict) -> list[FlagData]:
        confidence = facts.get("confidence")
        if confidence is not None and confidence < self.threshold:
            return [FlagData(
                rule="LowConfidenceMerge",
                severity="Medium",
                message=(
                    f"Farmer {farmer_id} merged with low confidence {confidence:.2f} "
                    f"(threshold {self.threshold})"
                ),
            )]
        return []
