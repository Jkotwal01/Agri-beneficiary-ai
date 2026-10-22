"""ProfileService — save a farmer's profile, score completeness, link to a golden record."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.eligibility.engine import evaluate_all
from app.models.enrollment import Enrollment
from app.models.farmer_profile import FarmerProfile
from app.models.recommendation import Recommendation
from app.models.scheme import Scheme
from app.models.scheme_application import SchemeApplication
from app.profiles.completeness import score
from app.profiles.profile_linker import link


class ProfileService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def save_profile(self, user_id: int, payload: dict) -> FarmerProfile:
        db = self._db
        profile = (
            db.query(FarmerProfile).filter(FarmerProfile.user_id == user_id).first()
        )
        if profile is None:
            profile = FarmerProfile(user_id=user_id)
            db.add(profile)

        for key, value in payload.items():
            if hasattr(profile, key) and key not in ("id", "user_id"):
                setattr(profile, key, value)

        db.flush()
        profile.completeness = score(profile)

        if profile.farmer_id is None:
            farmer_id, _method, _score = link(db, profile)
            if farmer_id is not None:
                profile.farmer_id = farmer_id

        db.commit()
        db.refresh(profile)
        return profile

    def recommended_schemes(self, profile: FarmerProfile) -> list[dict]:
        """Eligible, not-yet-enrolled schemes whose domain the farmer opted into."""
        interests = set(profile.interests or [])

        if profile.farmer_id is not None:
            return self._recommended_from_recommendations(profile, interests)
        return self._recommended_live(profile, interests)

    def _enrolled_scheme_ids_via_applications(self, profile: FarmerProfile) -> set[int]:
        rows = (
            self._db.query(SchemeApplication.scheme_id)
            .filter(
                SchemeApplication.farmer_profile_id == profile.id,
                SchemeApplication.status.in_(["submitted", "approved"]),
            )
            .all()
        )
        return {r[0] for r in rows}

    def _recommended_from_recommendations(
        self, profile: FarmerProfile, interests: set[str]
    ) -> list[dict]:
        db = self._db
        rows = (
            db.query(Recommendation, Scheme)
            .join(Scheme, Scheme.id == Recommendation.scheme_id)
            .filter(
                Recommendation.farmer_id == profile.farmer_id,
                Recommendation.eligible.is_(True),
                Recommendation.already_enrolled.is_(False),
            )
            .all()
        )
        excluded = self._enrolled_scheme_ids_via_applications(profile)
        return [
            {
                "scheme_id": scheme.id,
                "scheme_code": scheme.code,
                "scheme_name": scheme.name,
            }
            for _rec, scheme in rows
            if scheme.id not in excluded
            and (not interests or scheme.domain in interests)
        ]

    def _recommended_live(
        self, profile: FarmerProfile, interests: set[str]
    ) -> list[dict]:
        db = self._db
        facts = {
            "total_land_ha": profile.total_land_ha or 0.0,
            "crop": (profile.main_crops or [None])[0],
        }
        results = evaluate_all(facts)
        eligible_codes = {r.scheme for r in results if r.eligible}

        enrolled_codes: set[str] = set()
        if profile.farmer_id is not None:
            enrolled_codes = {
                s.code
                for s, in db.query(Scheme.code)
                .join(Enrollment, Enrollment.scheme_id == Scheme.id)
                .filter(Enrollment.farmer_id == profile.farmer_id)
                .all()
            }

        schemes = db.query(Scheme).filter(Scheme.code.in_(eligible_codes)).all()
        return [
            {"scheme_id": s.id, "scheme_code": s.code, "scheme_name": s.name}
            for s in schemes
            if s.code not in enrolled_codes and (not interests or s.domain in interests)
        ]
