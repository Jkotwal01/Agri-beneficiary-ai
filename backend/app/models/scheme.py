from sqlalchemy import Column, Date, Integer, String

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
