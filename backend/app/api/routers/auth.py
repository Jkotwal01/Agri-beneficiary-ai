"""Auth router — POST /auth/register, POST /auth/login."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import create_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

VALID_ROLES = {"admin", "officer", "farmer"}


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):  # noqa: B008
    """Self-signup for farmers; admin/officer accounts must be created by admin."""
    if payload.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400, detail=f"Invalid role. Choose from {VALID_ROLES}"
        )

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token({"sub": str(user.id), "role": user.role, "email": user.email})
    return TokenResponse(access_token=token, role=user.role)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):  # noqa: B008
    """Authenticate a user and return a JWT."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_token({"sub": str(user.id), "role": user.role, "email": user.email})
    return TokenResponse(access_token=token, role=user.role)
