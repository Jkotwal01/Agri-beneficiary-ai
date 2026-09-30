from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.core.db import Base


class SourceRecord(Base):
    __tablename__ = "source_records"
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String, index=True, nullable=False)
    source_row_id = Column(String, nullable=False)
    raw_json = Column(JSONB, nullable=False)
    loaded_at = Column(DateTime(timezone=True), server_default=func.now())
