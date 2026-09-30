from sqlalchemy import Column, Float, ForeignKey, Integer, String

from app.core.db import Base


class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    season = Column(String)
    amount = Column(Float)
    source_record_id = Column(Integer, ForeignKey("source_records.id"))
