"""Pydantic schemas for auth endpoints."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "farmer"  # farmer | officer | admin


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class UserOut(BaseModel):
    id: int
    email: str
    role: str

    model_config = {"from_attributes": True}
