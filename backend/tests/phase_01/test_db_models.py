import pytest
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.core.db import Base, engine
from app.models.clean_record import CleanRecord
from app.models.email_log import EmailLog
from app.models.farmer import Farmer
from app.models.farmer_profile import FarmerProfile
from app.models.flag import Flag
from app.models.match_candidate import MatchCandidate
from app.models.scheme import Scheme
from app.models.scheme_application import SchemeApplication
from app.models.source_record import SourceRecord
from app.models.user import User
from app.repositories.application_repo import ApplicationRepo
from app.repositories.base import BaseRepository
from app.repositories.clean_record_repo import CleanRecordRepo
from app.repositories.email_log_repo import EmailLogRepo
from app.repositories.farmer_repo import FarmerRepo
from app.repositories.flag_repo import FlagRepo
from app.repositories.match_repo import MatchRepo
from app.repositories.profile_repo import ProfileRepo

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db_session():
    # We assume alembic upgrade head has been run or we can create all here
    # For testing, we can just create_all
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_insert_and_retrieve_all_models(db_session):
    # User
    user = User(email="test@test.com", password_hash="hash", role="admin")
    BaseRepository(User, db_session).save(user)

    # Farmer
    farmer_repo = FarmerRepo(db_session)
    f = Farmer(name="Test Farmer", mobile="1234567890")
    farmer_repo.save(f)

    # Source Record
    sr = SourceRecord(source_name="pmkisan", source_row_id="1", raw_json={"a": 1})
    BaseRepository(SourceRecord, db_session).save(sr)

    # Clean Record
    cr_repo = CleanRecordRepo(db_session)
    cr = CleanRecord(source_record_id=sr.id, name_norm="test farmer")
    cr_repo.save(cr)

    # Match Candidate
    mr_repo = MatchRepo(db_session)
    mc = MatchCandidate(record_a=cr.id, record_b=cr.id, score=0.9, decision="review")
    mr_repo.save(mc)

    # Scheme
    scheme = Scheme(code="PMK", name="PM Kisan")
    BaseRepository(Scheme, db_session).save(scheme)

    # Flag
    flag_repo = FlagRepo(db_session)
    flag = Flag(
        farmer_id=f.id, type="test", severity="low", reason="test", status="open"
    )
    flag_repo.save(flag)

    # Profile
    prof_repo = ProfileRepo(db_session)
    prof = FarmerProfile(user_id=user.id, full_name="Test")
    prof_repo.save(prof)

    # Scheme Application
    app_repo = ApplicationRepo(db_session)
    sapp = SchemeApplication(
        farmer_profile_id=prof.id, scheme_id=scheme.id, status="draft"
    )
    app_repo.save(sapp)

    # Email Log
    elog_repo = EmailLogRepo(db_session)
    elog = EmailLog(farmer_profile_id=prof.id, type="digest")
    elog_repo.save(elog)

    assert farmer_repo.get(f.id).name == "Test Farmer"
    assert cr_repo.get(cr.id).name_norm == "test farmer"
    assert mr_repo.get(mc.id).score == 0.9
    assert flag_repo.get(flag.id).type == "test"
    assert prof_repo.get(prof.id).full_name == "Test"
    assert app_repo.get(sapp.id).status == "draft"
    assert elog_repo.get(elog.id).type == "digest"


def test_indexes_exist(db_session):
    # Verify indexes from Section 5
    result = db_session.execute(
        text("SELECT indexname FROM pg_indexes WHERE schemaname = 'public'")
    ).fetchall()
    indexes = [r[0] for r in result]

    assert "ix_clean_records_dist_phone" in indexes
    assert "ix_clean_records_mobile10" in indexes
    assert "ix_clean_records_vill_surv" in indexes
    assert "ix_flags_status_type" in indexes
