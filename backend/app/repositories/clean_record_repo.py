from sqlalchemy.orm import Session

from app.models.clean_record import CleanRecord
from app.repositories.base import BaseRepository


class CleanRecordRepo(BaseRepository[CleanRecord]):
    def __init__(self, db: Session):
        super().__init__(CleanRecord, db)
