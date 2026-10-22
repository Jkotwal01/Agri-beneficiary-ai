"""DuplicateRule ABC — all 5 rule classes implement this interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class FlagData:
    rule: str
    severity: str  # High | Medium | Low
    message: str


class DuplicateRule(ABC):
    @abstractmethod
    def check(self, farmer_id: int, facts: dict) -> list[FlagData]:
        """Return list of FlagData (empty = no violation)."""
