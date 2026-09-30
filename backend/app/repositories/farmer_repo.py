from sqlalchemy.orm import Session

from app.models.farmer import Farmer
from app.repositories.base import BaseRepository


class FarmerRepo(BaseRepository[Farmer]):
    def __init__(self, db: Session):
        super().__init__(Farmer, db)
