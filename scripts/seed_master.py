"""
Master Seed Script — populates essential reference catalogs (schemes) and
default test user accounts (Admin, Officer, Farmer) required for real-data testing.

Usage (from repo root):
    python scripts/seed_master.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow importing backend modules from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.scheme import Scheme
from app.models.user import User


def seed_master() -> None:
    db = SessionLocal()
    try:
        # 1. Seed Schemes Catalog
        schemes = [
            Scheme(
                code="PM_KISAN",
                name="PM-KISAN",
                domain="AGRICULTURE",
                description="Income support of Rs. 6000/yr for small and marginal farmers.",
                status="active",
                benefit_score=10,
            ),
            Scheme(
                code="PMFBY",
                name="PMFBY (Crop Insurance)",
                domain="INSURANCE",
                description="Pradhan Mantri Fasal Bima Yojana crop loss and insurance protection.",
                status="active",
                benefit_score=8,
            ),
            Scheme(
                code="KCC",
                name="Kisan Credit Card",
                domain="CREDIT",
                description="Concessional institutional credit and low-interest crop loans.",
                status="active",
                benefit_score=9,
            ),
            Scheme(
                code="NFSM",
                name="National Food Security Mission",
                domain="AGRICULTURE",
                description="Subsidized high-yielding seed distribution and farm machinery support.",
                status="active",
                benefit_score=6,
            ),
        ]

        schemes_added = 0
        for s in schemes:
            existing = db.query(Scheme).filter(Scheme.code == s.code).first()
            if not existing:
                db.add(s)
                schemes_added += 1

        # 2. Seed Default Role Accounts
        users = [
            User(
                email="admin@agri.gov.in",
                password_hash=hash_password("Admin@123"),
                role="admin",
            ),
            User(
                email="officer@agri.gov.in",
                password_hash=hash_password("Officer@123"),
                role="officer",
            ),
            User(
                email="farmer@agri.gov.in",
                password_hash=hash_password("Farmer@123"),
                role="farmer",
            ),
        ]

        users_added = 0
        for u in users:
            existing = db.query(User).filter(User.email == u.email).first()
            if not existing:
                db.add(u)
                users_added += 1

        db.commit()
        print(
            f"[seed_master] Success: {schemes_added} schemes added, {users_added} users added."
        )
    finally:
        db.close()


if __name__ == "__main__":
    seed_master()
