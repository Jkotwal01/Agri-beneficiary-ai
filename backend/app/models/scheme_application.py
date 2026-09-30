from sqlalchemy import ARRAY, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.core.db import Base


class SchemeApplication(Base):
    __tablename__ = "scheme_applications"
    id = Column(Integer, primary_key=True, index=True)
    farmer_profile_id = Column(
        Integer, ForeignKey("farmer_profiles.id"), nullable=False
    )
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    status = Column(String, nullable=False)
    form_data = Column(JSONB)
    autofilled_keys = Column(ARRAY(String))
    submitted_at = Column(DateTime(timezone=True))
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    officer_note = Column(String)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
