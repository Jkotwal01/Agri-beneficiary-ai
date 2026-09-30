import os

models_dir = "backend/app/models"
repos_dir = "backend/app/repositories"

models = {
    "__init__.py": """from app.core.db import Base
from .source_record import SourceRecord
from .clean_record import CleanRecord
from .match_candidate import MatchCandidate
from .farmer import Farmer
from .farmer_link import FarmerLink
from .land_parcel import LandParcel
from .scheme import Scheme
from .enrollment import Enrollment
from .flag import Flag
from .recommendation import Recommendation
from .user import User
from .audit_log import AuditLog
from .farmer_profile import FarmerProfile
from .scheme_application import SchemeApplication
from .email_log import EmailLog
""",
    "source_record.py": """from sqlalchemy import Column, String, Integer, DateTime
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
""",
    "clean_record.py": """from sqlalchemy import Column, String, Integer, Float, ForeignKey, Index
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
""",
    "match_candidate.py": """from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from app.core.db import Base

class MatchCandidate(Base):
    __tablename__ = "match_candidates"
    id = Column(Integer, primary_key=True, index=True)
    record_a = Column(Integer, ForeignKey("clean_records.id"), nullable=False)
    record_b = Column(Integer, ForeignKey("clean_records.id"), nullable=False)
    score = Column(Float, nullable=False)
    decision = Column(String, nullable=False) # auto_link / review / no_match
    features_json = Column(JSONB)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
""",
    "farmer.py": """from sqlalchemy import Column, String, Integer, Float
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
""",
    "farmer_link.py": """from sqlalchemy import Column, String, Integer, Float, ForeignKey
from app.core.db import Base

class FarmerLink(Base):
    __tablename__ = "farmer_links"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False, index=True)
    clean_record_id = Column(Integer, ForeignKey("clean_records.id"), nullable=False)
    method = Column(String, nullable=False)
    score = Column(Float)
""",
    "land_parcel.py": """from sqlalchemy import Column, String, Integer, Float, ForeignKey
from app.core.db import Base

class LandParcel(Base):
    __tablename__ = "land_parcels"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False, index=True)
    village_code = Column(String, nullable=False)
    survey_no = Column(String, nullable=False)
    area_ha = Column(Float, nullable=False)
""",
    "scheme.py": """from sqlalchemy import Column, String, Integer, Date
from app.core.db import Base

class Scheme(Base):
    __tablename__ = "schemes"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    benefit_score = Column(Integer, nullable=False, default=0)
    domain = Column(String)
    status = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
""",
    "enrollment.py": """from sqlalchemy import Column, String, Integer, Float, ForeignKey
from app.core.db import Base

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    season = Column(String)
    amount = Column(Float)
    source_record_id = Column(Integer, ForeignKey("source_records.id"))
""",
    "flag.py": """from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Index
from sqlalchemy.sql import func
from app.core.db import Base

class Flag(Base):
    __tablename__ = "flags"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False, index=True)
    type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String, nullable=False) # open / confirmed / dismissed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_by = Column(Integer, ForeignKey("users.id"))
    
    __table_args__ = (
        Index("ix_flags_status_type", "status", "type"),
    )
""",
    "recommendation.py": """from sqlalchemy import Column, String, Integer, Boolean
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
""",
    "user.py": """from sqlalchemy import Column, String, Integer
from app.core.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False) # admin / officer / farmer
""",
    "audit_log.py": """from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from app.core.db import Base

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String, nullable=False)
    entity = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    at = Column(DateTime(timezone=True), server_default=func.now())
""",
    "farmer_profile.py": """from sqlalchemy import Column, String, Integer, Boolean, Float, ForeignKey, ARRAY
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
""",
    "scheme_application.py": """from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.db import Base

class SchemeApplication(Base):
    __tablename__ = "scheme_applications"
    id = Column(Integer, primary_key=True, index=True)
    farmer_profile_id = Column(Integer, ForeignKey("farmer_profiles.id"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=False)
    status = Column(String, nullable=False)
    form_data = Column(JSONB)
    autofilled_keys = Column(ARRAY(String))
    submitted_at = Column(DateTime(timezone=True))
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    officer_note = Column(String)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
""",
    "email_log.py": """from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.db import Base

class EmailLog(Base):
    __tablename__ = "email_log"
    id = Column(Integer, primary_key=True, index=True)
    farmer_profile_id = Column(Integer, ForeignKey("farmer_profiles.id"), nullable=False)
    scheme_id = Column(Integer, ForeignKey("schemes.id"))
    type = Column(String, nullable=False) # digest / alert / reminder / status
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
"""
}

repos = {
    "__init__.py": "",
    "base.py": """from typing import TypeVar, Generic, Type, Any, Optional
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: Any) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def save(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
""",
    "farmer_repo.py": """from sqlalchemy.orm import Session
from app.models.farmer import Farmer
from app.repositories.base import BaseRepository

class FarmerRepo(BaseRepository[Farmer]):
    def __init__(self, db: Session):
        super().__init__(Farmer, db)
""",
    "clean_record_repo.py": """from sqlalchemy.orm import Session
from app.models.clean_record import CleanRecord
from app.repositories.base import BaseRepository

class CleanRecordRepo(BaseRepository[CleanRecord]):
    def __init__(self, db: Session):
        super().__init__(CleanRecord, db)
""",
    "match_repo.py": """from sqlalchemy.orm import Session
from app.models.match_candidate import MatchCandidate
from app.repositories.base import BaseRepository

class MatchRepo(BaseRepository[MatchCandidate]):
    def __init__(self, db: Session):
        super().__init__(MatchCandidate, db)
""",
    "flag_repo.py": """from sqlalchemy.orm import Session
from app.models.flag import Flag
from app.repositories.base import BaseRepository

class FlagRepo(BaseRepository[Flag]):
    def __init__(self, db: Session):
        super().__init__(Flag, db)
""",
    "profile_repo.py": """from sqlalchemy.orm import Session
from app.models.farmer_profile import FarmerProfile
from app.repositories.base import BaseRepository

class ProfileRepo(BaseRepository[FarmerProfile]):
    def __init__(self, db: Session):
        super().__init__(FarmerProfile, db)
""",
    "application_repo.py": """from sqlalchemy.orm import Session
from app.models.scheme_application import SchemeApplication
from app.repositories.base import BaseRepository

class ApplicationRepo(BaseRepository[SchemeApplication]):
    def __init__(self, db: Session):
        super().__init__(SchemeApplication, db)
""",
    "email_log_repo.py": """from sqlalchemy.orm import Session
from app.models.email_log import EmailLog
from app.repositories.base import BaseRepository

class EmailLogRepo(BaseRepository[EmailLog]):
    def __init__(self, db: Session):
        super().__init__(EmailLog, db)
"""
}

for name, content in models.items():
    with open(os.path.join(models_dir, name), "w") as f:
        f.write(content)

for name, content in repos.items():
    with open(os.path.join(repos_dir, name), "w") as f:
        f.write(content)
