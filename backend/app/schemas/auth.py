"""
schemas/auth.py
---------------
Pydantic v2 request/response models for authentication.

No imports from teammates — this file is fully standalone.
Dev 3 (frontend) depends on TokenResponse shape for login API calls.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator

# ── Shared password validator ─────────────────────────────────────────────────


def _validate_password(v: str) -> str:
    """
    Single source of truth for password strength.
    Collects ALL failures so user knows everything to fix at once.

    Rules:
      - Minimum 8 characters
      - At least one number       (0-9)
      - At least one uppercase    (A-Z)
      - At least one lowercase    (a-z)
    """
    errors = []
    if len(v) < 8:
        errors.append("at least 8 characters")
    if not any(c.isdigit() for c in v):
        errors.append("at least one number (0-9)")
    if not any(c.isupper() for c in v):
        errors.append("at least one uppercase letter (A-Z)")
    if not any(c.islower() for c in v):
        errors.append("at least one lowercase letter (a-z)")
    if errors:
        raise ValueError(f"Password must contain: {', '.join(errors)}")
    return v


# ── Request Models ────────────────────────────────────────────────────────────


class UserRegister(BaseModel):
    """Body for POST /api/auth/register"""

    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(v) > 50:
            raise ValueError("Username must be 50 characters or fewer")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, _ and -")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return _validate_password(v)


class UserLogin(BaseModel):
    """Body for POST /api/auth/login"""

    email: EmailStr
    password: str


class PasswordChange(BaseModel):
    """
    Body for POST /api/auth/change-password.
    User must be logged in (JWT required).

    Rules enforced in security.py:
      - current_password must match what's stored in DB
      - new_password must differ from current_password
      - new_password must meet strength requirements
      - confirm_password must match new_password (checked here)
    """

    current_password: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def new_password_strength(cls, v: str) -> str:
        return _validate_password(v)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


# ── Response Models ─────────────────────────────────────────────────────────


class UserRead(BaseModel):
    """
    Returned after register, login, and GET /api/auth/me.
    Dev 3: use this shape to display user info in the UI.
    """

    id: UUID
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime

    # Allows constructing from SQLAlchemy ORM objects directly
    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """
    Returned by POST /api/auth/login.
    Dev 3: store access_token and send as:
        Authorization: Bearer <access_token>
    """

    access_token: str
    token_type: str = "bearer"
    user: UserRead


class PasswordChangeResponse(BaseModel):
    """
    Returned by POST /api/auth/change-password.
    A fresh token is issued so the user stays logged in immediately.
    Dev 3: replace the stored access_token with the new one.
    """

    message: str = "Password changed successfully"
    access_token: str  # fresh token — old one is effectively invalidated
    token_type: str = "bearer"
