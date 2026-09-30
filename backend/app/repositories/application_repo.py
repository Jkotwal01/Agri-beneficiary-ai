from sqlalchemy.orm import Session

from app.models.scheme_application import SchemeApplication
from app.repositories.base import BaseRepository


class ApplicationRepo(BaseRepository[SchemeApplication]):
    def __init__(self, db: Session):
        super().__init__(SchemeApplication, db)
