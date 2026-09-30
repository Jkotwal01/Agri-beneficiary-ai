from sqlalchemy.orm import Session

from app.models.match_candidate import MatchCandidate
from app.repositories.base import BaseRepository


class MatchRepo(BaseRepository[MatchCandidate]):
    def __init__(self, db: Session):
        super().__init__(MatchCandidate, db)
