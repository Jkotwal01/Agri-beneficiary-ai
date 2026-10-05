"""JWT security helpers — hash_password, verify_password, create_token, decode_token."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def hash_password(plain: str) -> str:
    """Return bcrypt hash of the given plaintext password."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored bcrypt hash."""
    return _pwd_context.verify(plain, hashed)


def create_token(data: dict[str, Any], expires_minutes: int | None = None) -> str:
    """Create a signed JWT with an exp claim."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.JWT_EXPIRE_MINUTES
    )
    payload = {**data, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT.
    Raises jose.JWTError on invalid/expired tokens.
    """
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])


__all__ = [
    "JWTError",
    "create_token",
    "decode_token",
    "hash_password",
    "verify_password",
]
