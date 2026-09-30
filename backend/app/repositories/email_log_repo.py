from sqlalchemy.orm import Session

from app.models.email_log import EmailLog
from app.repositories.base import BaseRepository


class EmailLogRepo(BaseRepository[EmailLog]):
    def __init__(self, db: Session):
        super().__init__(EmailLog, db)
