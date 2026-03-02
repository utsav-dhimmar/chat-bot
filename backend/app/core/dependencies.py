"""
core/dependencies.py
--------------------
FastAPI dependency — injects the authenticated user into any route.

Uses HTTPBearer so the /docs Authorize button simply asks:
  "Enter your token"  →  paste the token from /login response
  (no username/password form confusion)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.models import User
from app.db.session import get_db

# HTTPBearer reads the  Authorization: Bearer <token>  header
# auto_error=False lets us give a cleaner error message ourselves
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Read Bearer token → decode JWT → fetch user from DB → return User.

    Raises HTTP 401 if:
      - No Authorization header at all
      - Token is malformed or expired
      - User ID not found in DB
      - Account is deactivated
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials — login and use the token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # No token provided at all
    if not credentials:
        raise credentials_exc

    try:
        user_id = decode_token(credentials.credentials)
    except JWTError:
        raise credentials_exc

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exc

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    return user


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Same as get_current_user but also checks is_admin = True.
    Use this on every admin route.

    Raises HTTP 403 if user is not an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
