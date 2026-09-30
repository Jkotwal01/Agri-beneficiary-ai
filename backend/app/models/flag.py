from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.sql import func

from app.core.db import Base


class Flag(Base):
    __tablename__ = "flags"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False, index=True)
    type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String, nullable=False) # open / confirmed / dismissed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_by = Column(Integer, ForeignKey("users.id"))
    
    __table_args__ = (
        Index("ix_flags_status_type", "status", "type"),
    )
