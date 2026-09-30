from sqlalchemy import ARRAY, Boolean, Column, Float, ForeignKey, Integer, String

from app.core.db import Base


class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"))
    full_name = Column(String)
    father_name = Column(String)
    dob = Column(String)
    gender = Column(String)
    mobile = Column(String)
    email = Column(String)
    category = Column(String)
    village = Column(String)
    taluka = Column(String)
    district = Column(String)
    state = Column(String)
    pincode = Column(String)
    total_land_ha = Column(Float)
    ownership_type = Column(String)
    main_crops = Column(ARRAY(String))
    irrigation_type = Column(String)
    interests = Column(ARRAY(String))
    agristack_id = Column(String)
    bank_name = Column(String)
    ifsc = Column(String)
    email_opt_in = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    completeness = Column(Integer, default=0)
