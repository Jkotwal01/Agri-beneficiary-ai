# Dependency wiring — wired per phase; only add here, never in routers directly.
from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import get_db as _get_db
from app.core.security import JWTError, decode_token
from app.models.user import User

# Re-export so routers import from one place
get_db = _get_db

_bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),  # noqa: B008
    db: Session = Depends(_get_db),  # noqa: B008
) -> User:
    """Extract and validate the JWT; return the authenticated User."""
    token = credentials.credentials
    try:
        payload = decode_token(token)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


def require_role(*roles: str) -> Callable:
    """Return a FastAPI dependency that enforces one of the given roles."""

    def _check(current_user: User = Depends(get_current_user)) -> User:  # noqa: B008
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' is not allowed here",
            )
        return current_user

    return _check


__all__ = ["Session", "get_current_user", "get_db", "require_role"]
