from sqlalchemy.orm import Session

from app.models.farmer_profile import FarmerProfile
from app.repositories.base import BaseRepository


class ProfileRepo(BaseRepository[FarmerProfile]):
    def __init__(self, db: Session):
        super().__init__(FarmerProfile, db)
