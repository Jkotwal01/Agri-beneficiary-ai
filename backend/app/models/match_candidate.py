from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from app.core.db import Base


class MatchCandidate(Base):
    __tablename__ = "match_candidates"
    id = Column(Integer, primary_key=True, index=True)
    record_a = Column(Integer, ForeignKey("clean_records.id"), nullable=False)
    record_b = Column(Integer, ForeignKey("clean_records.id"), nullable=False)
    score = Column(Float, nullable=False)
    decision = Column(String, nullable=False)  # auto_link / review / no_match
    features_json = Column(JSONB)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
