from sqlalchemy import Column, Float, ForeignKey, Integer, String

from app.core.db import Base


class FarmerLink(Base):
    __tablename__ = "farmer_links"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False, index=True)
    clean_record_id = Column(Integer, ForeignKey("clean_records.id"), nullable=False)
    method = Column(String, nullable=False)
    score = Column(Float)
