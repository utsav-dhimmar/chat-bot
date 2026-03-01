"""
api/auth.py
-----------
Authentication routes.

Endpoints:
  POST /api/auth/register        - create account
  POST /api/auth/login           - login with JSON  { email, password }
  GET  /api/auth/me              - get current user (token required)
  POST /api/auth/change-password - change password  (token required)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.security import (
    change_password,
    create_access_token,
    hash_and_encrypt_password,
    verify_password,
)
from app.db.models import User
from app.db.session import get_db
from app.schemas.auth import (
    PasswordChange,
    PasswordChangeResponse,
    TokenResponse,
    UserLogin,
    UserRead,
    UserRegister,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ── Register ──────────────────────────────────────────────────────────────────


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Create a new user account.

    Body: { "username": "...", "email": "...", "password": "..." }
    """
    existing_email = await db.execute(select(User).where(User.email == body.email))
    if existing_email.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists",
        )

    existing_name = await db.execute(select(User).where(User.username == body.username))
    if existing_name.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken",
        )

    user = User(
        username=body.username,
        email=body.email,
        hashed_password=hash_and_encrypt_password(body.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


# ── Login ─────────────────────────────────────────────────────────────────────


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login with email + password.

    Body: { "email": "...", "password": "..." }

    Returns: { "access_token": "...", "token_type": "bearer", "user": {...} }

    HOW TO USE THE TOKEN IN /docs:
      1. Copy the access_token value from the response
      2. Click the lock icon (Authorize) at the top right of /docs
      3. Paste the token in the  Value  field  (just the token, no "Bearer" prefix)
      4. Click Authorize — all protected endpoints will now work
    """
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    token = create_access_token(str(user.id))
    return TokenResponse(
        access_token=token,
        user=UserRead.model_validate(user),
    )


# ── Get current user ──────────────────────────────────────────────────────────


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently logged-in user's profile. Requires token."""
    return current_user


# ── Change password ───────────────────────────────────────────────────────────


@router.post("/change-password", response_model=PasswordChangeResponse)
async def change_password_route(
    body: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Change password. Requires current password for verification.

    Body: { "current_password": "...", "new_password": "...", "confirm_password": "..." }

    Returns a fresh token — update the stored token on the frontend.
    """
    new_stored = change_password(
        current_plain=body.current_password,
        new_plain=body.new_password,
        stored_value=current_user.hashed_password,
    )

    current_user.hashed_password = new_stored
    db.add(current_user)

    new_token = create_access_token(str(current_user.id))

    return PasswordChangeResponse(
        message="Password changed successfully",
        access_token=new_token,
    )
