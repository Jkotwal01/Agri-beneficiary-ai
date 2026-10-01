"""
pytest conftest.py — sets a fallback DATABASE_URL so tests run locally
without needing to export it manually every time.

In CI, the DATABASE_URL env var is set by the workflow and takes precedence.
"""

import os

# Set a test DB default so local `pytest` works without exporting env vars.
# CI always provides DATABASE_URL explicitly via workflow env: block.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres",
)
os.environ.setdefault("JWT_SECRET", "local-dev-test-secret")
