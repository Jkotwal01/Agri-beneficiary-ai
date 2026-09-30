from sqlalchemy import Column, Float, Integer, String

from app.core.db import Base


class Farmer(Base):
    __tablename__ = "farmers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    father_name = Column(String)
    dob = Column(String)
    mobile = Column(String)
    village_code = Column(String)
    district_code = Column(String)
    total_land_ha = Column(Float)
    category = Column(String)
    confidence = Column(Float)
