"""
Seed realistic Farmer Profiles & Scheme Applications for flagged and normal farmers
so the Officer Inbox has real, rich, interactive beneficiary dossiers.
"""

from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta

from app.core.db import SessionLocal
from app.models.farmer import Farmer
from app.models.farmer_profile import FarmerProfile
from app.models.flag import Flag
from app.models.scheme import Scheme
from app.models.scheme_application import SchemeApplication
from app.models.user import User


def seed_applications():
    db = SessionLocal()
    try:
        schemes = db.query(Scheme).all()
        if not schemes:
            print("No schemes found. Cannot seed applications.")
            return

        scheme_map = {s.code: s for s in schemes}

        # 1. Get first 35 distinct farmer_ids that have flags
        flagged_farmer_ids = [
            f_id for (f_id,) in db.query(Flag.farmer_id).distinct().limit(35).all()
        ]

        # 2. Get 15 clean farmers (without flags)
        all_flagged_set = set(flagged_farmer_ids)
        clean_farmers = (
            db.query(Farmer).filter(~Farmer.id.in_(all_flagged_set)).limit(15).all()
        )
        clean_farmer_ids = [f.id for f in clean_farmers]

        target_farmer_ids = flagged_farmer_ids + clean_farmer_ids
        print(f"Targeting {len(target_farmer_ids)} farmers for application seeding...")

        created_apps = 0
        now = datetime.now(UTC)

        for idx, farmer_id in enumerate(target_farmer_ids):
            farmer = db.get(Farmer, farmer_id)
            if not farmer:
                continue

            # Check / create User
            email = f"farmer_{farmer.id}@agri.gov.in"
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    email=email,
                    password_hash="system_seed_farmer",
                    role="farmer",
                )
                db.add(user)
                db.flush()

            # Check / create FarmerProfile
            profile = (
                db.query(FarmerProfile).filter(FarmerProfile.user_id == user.id).first()
            )
            if not profile:
                profile = FarmerProfile(
                    user_id=user.id,
                    farmer_id=farmer.id,
                    full_name=farmer.name.title(),
                    father_name=(
                        farmer.father_name.title()
                        if farmer.father_name
                        else f"Govind {farmer.name.split()[-1].title()}"
                    ),
                    dob=farmer.dob or "1978-08-15",
                    gender="Male" if idx % 3 != 0 else "Female",
                    mobile=farmer.mobile or f"98230{farmer.id:05d}",
                    email=email,
                    category=farmer.category
                    or ("Small & Marginal" if idx % 2 == 0 else "General"),
                    village=farmer.village_code or "Ralegaon",
                    taluka="Yavatmal",
                    district=farmer.district_code or "Nagpur",
                    state="Maharashtra",
                    pincode="445001",
                    total_land_ha=farmer.total_land_ha
                    or round(random.uniform(1.2, 4.5), 2),
                    ownership_type="Individual Ownership",
                    main_crops=["Soybean", "Cotton", "Paddy"],
                    irrigation_type="Canal / Well",
                    interests=[
                        "Direct Benefit Transfer",
                        "Subsidies",
                        "Crop Insurance",
                    ],
                    agristack_id=f"AGRI-MH-{farmer.id:06d}",
                    bank_name="State Bank of India",
                    ifsc="SBIN0004521",
                    email_opt_in=True,
                    verified=True,
                    completeness=95,
                )
                db.add(profile)
                db.flush()

            # Check if an application already exists for this profile
            existing_app = (
                db.query(SchemeApplication)
                .filter(SchemeApplication.farmer_profile_id == profile.id)
                .first()
            )
            if existing_app:
                continue

            # Choose scheme based on flag type or random
            flag = db.query(Flag).filter(Flag.farmer_id == farmer.id).first()
            if flag and "PMKISAN" in flag.type.upper():
                chosen_scheme = scheme_map.get("PM_KISAN", schemes[0])
            elif flag and "PMFBY" in flag.type.upper():
                chosen_scheme = scheme_map.get("PMFBY", schemes[0])
            else:
                chosen_scheme = schemes[idx % len(schemes)]

            submitted_days_ago = random.randint(1, 14)
            submitted_time = now - timedelta(
                days=submitted_days_ago, hours=random.randint(1, 12)
            )

            # Decide status: 70% submitted (pending review), 15% approved, 15% rejected
            status_dice = random.random()
            if status_dice < 0.70:
                app_status = "submitted"
                officer_note = None
                reviewed_by = None
            elif status_dice < 0.85:
                app_status = "approved"
                officer_note = (
                    "All land holding documents verified with AgriStack geo-registry."
                )
                reviewed_by = 1
            else:
                app_status = "rejected"
                officer_note = (
                    "Land holding ceiling exceeded according to survey records."
                )
                reviewed_by = 1

            form_data = {
                "full_name": profile.full_name,
                "mobile": profile.mobile,
                "father_name": profile.father_name,
                "category": profile.category,
                "total_land_ha": profile.total_land_ha,
                "survey_parcel_no": f"SRV-77/{farmer.id}",
                "village": profile.village,
                "district": profile.district,
                "state": profile.state,
                "bank_name": profile.bank_name,
                "ifsc": profile.ifsc,
                "crop_name": "Soybean" if "PMFBY" in chosen_scheme.code else None,
                "insured_sum": 54000 if "PMFBY" in chosen_scheme.code else None,
                "declaration": True,
            }

            app = SchemeApplication(
                farmer_profile_id=profile.id,
                scheme_id=chosen_scheme.id,
                status=app_status,
                form_data=form_data,
                autofilled_keys=[
                    "full_name",
                    "mobile",
                    "village",
                    "district",
                    "total_land_ha",
                    "bank_name",
                    "ifsc",
                ],
                submitted_at=submitted_time,
                reviewed_by=reviewed_by,
                officer_note=officer_note,
            )
            db.add(app)
            created_apps += 1

        db.commit()
        print(
            f"Successfully seeded {created_apps} realistic applications with profiles!"
        )

    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_applications()
