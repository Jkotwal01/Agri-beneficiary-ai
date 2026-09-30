from sqlalchemy.orm import Session

from app.models.flag import Flag
from app.repositories.base import BaseRepository


class FlagRepo(BaseRepository[Flag]):
    def __init__(self, db: Session):
        super().__init__(Flag, db)
