"""PreprocessingService — thin orchestration layer around PreprocessingPipeline."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.preprocessing.pipeline import PreprocessingPipeline


class PreprocessingService:
    def __init__(self, db: Session) -> None:
        self._pipeline = PreprocessingPipeline(db)

    def run(self) -> int:
        """Run the full preprocessing pipeline. Returns rows written."""
        return self._pipeline.run()
