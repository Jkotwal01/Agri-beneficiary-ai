"""Pipeline router — POST /pipeline/ingest (admin only, runs in background)."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.pipeline import PipelineResponse
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

DATA_DIR = Path("data/synthetic")


def _run_ingest(data_dir: Path, db: Session) -> None:
    svc = IngestionService(db)
    svc.ingest_all(data_dir)
    db.close()


@router.post("/ingest", response_model=PipelineResponse, status_code=202)
def ingest(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),  # noqa: B008
) -> PipelineResponse:
    """Trigger ingestion of all source CSVs into source_records (admin only)."""
    background_tasks.add_task(_run_ingest, DATA_DIR, db)
    return PipelineResponse(status="accepted")
