from sqlalchemy import Column, Float, ForeignKey, Index, Integer, String

from app.core.db import Base


class CleanRecord(Base):
    __tablename__ = "clean_records"
    id = Column(Integer, primary_key=True, index=True)
    source_record_id = Column(Integer, ForeignKey("source_records.id"), nullable=False)
    name_norm = Column(String)
    father_norm = Column(String)
    name_phonetic = Column(String)
    mobile10 = Column(String)
    village_code = Column(String)
    district_code = Column(String)
    dob = Column(String)
    survey_no = Column(String)
    bank_last4 = Column(String)
    land_ha = Column(Float)
    crop = Column(String)
    season = Column(String)

    __table_args__ = (
        Index("ix_clean_records_dist_phone", "district_code", "name_phonetic"),
        Index("ix_clean_records_mobile10", "mobile10"),
        Index("ix_clean_records_vill_surv", "village_code", "survey_no"),
    )
