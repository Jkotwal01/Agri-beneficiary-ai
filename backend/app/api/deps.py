# Dependency wiring — wired per phase; only add here, never in routers directly.
from sqlalchemy.orm import Session

from app.core.db import get_db as _get_db

# Re-export so routers import from one place
get_db = _get_db

__all__ = ["Session", "get_db"]
