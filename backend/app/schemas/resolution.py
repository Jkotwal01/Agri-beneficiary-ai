"""Resolution summary Pydantic schema."""

from __future__ import annotations

from pydantic import BaseModel


class ResolutionSummary(BaseModel):
    clean_records_processed: int
    candidate_pairs_evaluated: int
    auto_linked: int
    flagged_for_review: int
    no_match: int
    farmers_created: int
    chain_guard_blocked: int
