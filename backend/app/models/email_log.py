from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.core.db import Base


class EmailLog(Base):
    __tablename__ = "email_log"
    id = Column(Integer, primary_key=True, index=True)
    farmer_profile_id = Column(
        Integer, ForeignKey("farmer_profiles.id"), nullable=False
    )
    scheme_id = Column(Integer, ForeignKey("schemes.id"))
    type = Column(String, nullable=False)  # digest / alert / reminder / status
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
