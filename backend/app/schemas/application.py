"""Pydantic schemas for scheme applications."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class PrefillRequest(BaseModel):
    scheme_code: str


class FormFieldOut(BaseModel):
    key: str
    label: str
    type: str
    required: bool = False
    autofill_from: str | None = None


class PrefillResponse(BaseModel):
    values: dict[str, Any]
    autofilled_keys: list[str]
    fields: list[FormFieldOut]


class ApplicationSubmit(BaseModel):
    scheme_code: str
    form_data: dict[str, Any]


class ApplicationOut(BaseModel):
    id: int
    farmer_profile_id: int
    scheme_id: int
    status: str
    form_data: dict[str, Any] | None = None
    autofilled_keys: list[str] | None = None
    submitted_at: datetime | None = None
    reviewed_by: int | None = None
    officer_note: str | None = None

    # Enriched applicant & scheme details for real-world officer audits
    applicant_name: str | None = None
    father_name: str | None = None
    farmer_id: int | None = None
    mobile: str | None = None
    email: str | None = None
    village: str | None = None
    taluka: str | None = None
    district: str | None = None
    state: str | None = None
    category: str | None = None
    total_land_ha: float | None = None
    ownership_type: str | None = None
    main_crops: list[str] | None = None
    bank_name: str | None = None
    ifsc: str | None = None
    agristack_id: str | None = None
    scheme_name: str | None = None
    scheme_code: str | None = None
    flags_count: int = 0
    flags: list[dict[str, Any]] = []

    model_config = {"from_attributes": True}


class ApplicationDecisionIn(BaseModel):
    status: str  # approved | rejected
    note: str | None = None
