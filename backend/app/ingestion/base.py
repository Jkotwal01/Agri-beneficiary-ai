"""SourceAdapter abstract base class — Module 1 (Spec Section 6)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from pathlib import Path


class SourceAdapter(ABC):
    """One subclass per source CSV. Yields one common dict per row."""

    source_name: str  # must be set on each concrete adapter

    @abstractmethod
    def read(self, path: Path) -> Iterable[dict]:
        """Yield one normalised dict per source row."""
