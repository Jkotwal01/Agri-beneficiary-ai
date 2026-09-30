from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB

from app.core.db import Base


class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    eligible = Column(Boolean, nullable=False, default=False)
    reasons_json = Column(JSONB)
    already_enrolled = Column(Boolean, nullable=False, default=False)
    priority = Column(Integer, default=0)
