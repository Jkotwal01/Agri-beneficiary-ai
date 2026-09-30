from sqlalchemy import Column, Float, ForeignKey, Integer, String

from app.core.db import Base


class LandParcel(Base):
    __tablename__ = "land_parcels"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False, index=True)
    village_code = Column(String, nullable=False)
    survey_no = Column(String, nullable=False)
    area_ha = Column(Float, nullable=False)
