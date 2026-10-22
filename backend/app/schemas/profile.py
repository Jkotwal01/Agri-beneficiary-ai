"""Pydantic schemas for the farmer profile."""

from __future__ import annotations

from pydantic import BaseModel


class ProfileIn(BaseModel):
    full_name: str | None = None
    father_name: str | None = None
    dob: str | None = None
    gender: str | None = None
    mobile: str | None = None
    email: str | None = None
    category: str | None = None
    village: str | None = None
    taluka: str | None = None
    district: str | None = None
    state: str | None = None
    pincode: str | None = None
    total_land_ha: float | None = None
    ownership_type: str | None = None
    main_crops: list[str] | None = None
    irrigation_type: str | None = None
    interests: list[str] | None = None
    agristack_id: str | None = None
    bank_name: str | None = None
    ifsc: str | None = None
    email_opt_in: bool | None = None


class ProfileOut(ProfileIn):
    id: int
    user_id: int
    farmer_id: int | None = None
    verified: bool
    completeness: int

    model_config = {"from_attributes": True}


class RecommendedSchemeOut(BaseModel):
    scheme_id: int
    scheme_code: str
    scheme_name: str
