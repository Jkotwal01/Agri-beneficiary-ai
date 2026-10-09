"""Pipeline router — POST /pipeline/ingest and POST /pipeline/preprocess."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.pipeline import PipelineResponse
from app.services.ingestion_service import IngestionService
from app.services.preprocessing_service import PreprocessingService
from app.services.resolution_service import ResolutionService

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

DATA_DIR = Path("data/synthetic")


def _run_ingest(data_dir: Path, db: Session) -> None:
    svc = IngestionService(db)
    svc.ingest_all(data_dir)
    db.close()


def _run_preprocess(db: Session) -> None:
    svc = PreprocessingService(db)
    svc.run()
    db.close()


@router.post("/ingest", response_model=PipelineResponse, status_code=202)
def ingest(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),  # noqa: B008
) -> PipelineResponse:
    """Trigger ingestion of all source CSVs into source_records (admin only)."""
    background_tasks.add_task(_run_ingest, DATA_DIR, db)
    return PipelineResponse(status="accepted")


@router.post("/preprocess", response_model=PipelineResponse, status_code=202)
def preprocess(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),  # noqa: B008
) -> PipelineResponse:
    """Trigger preprocessing of source_records → clean_records (admin only)."""
    background_tasks.add_task(_run_preprocess, db)
    return PipelineResponse(status="accepted")


def _run_resolve(db: Session) -> None:
    svc = ResolutionService(db)
    svc.run()
    db.close()


@router.post("/resolve", response_model=PipelineResponse, status_code=202)
def resolve(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),  # noqa: B008
) -> PipelineResponse:
    """Trigger entity resolution: blocking → scoring → clustering → golden records."""
    background_tasks.add_task(_run_resolve, db)
    return PipelineResponse(status="accepted")
