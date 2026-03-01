"""
core/security.py
----------------
Two-layer password security + JWT token operations.

PASSWORD STORAGE STRATEGY (two layers):
  Layer 1 — bcrypt hashing  : one-way, can never be reversed
  Layer 2 — Fernet encryption: the bcrypt hash is then encrypted with
            a symmetric key (ENCRYPTION_KEY from config) before being
            stored in the database.

JWT:
  create_access_token() / decode_token() for stateless auth.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ── bcrypt context ──────────────────────────────────────────────────────────

# bcrypt cost factor 12 — strong, ~300ms per hash (good balance)
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _prepare_for_bcrypt(plain_password: str) -> str:
    """
    Pre-hash with SHA-256 before bcrypt.
    WHY: bcrypt silently truncates passwords over 72 bytes.
    """
    return hashlib.sha256(plain_password.encode("utf-8")).hexdigest()


def _get_fernet() -> Fernet:
    """
    Build a Fernet cipher from ENCRYPTION_KEY.
    """
    enc_key = settings.ENCRYPTION_KEY

    if not enc_key:
        # Dev-only fallback — warn loudly
        import warnings

        warnings.warn(
            "ENCRYPTION_KEY is not set! Using a random key. "
            "Passwords will NOT survive server restarts.",
            RuntimeWarning,
            stacklevel=3,
        )
        enc_key = Fernet.generate_key().decode()

    # Ensure it's bytes
    key_bytes = enc_key.encode() if isinstance(enc_key, str) else enc_key
    return Fernet(key_bytes)


# ── Two-layer password operations ───────────────────────────────────────────


def hash_and_encrypt_password(plain_password: str) -> str:
    """
    Layer 1: Hash with bcrypt
    Layer 2: Encrypt the hash with Fernet
    """
    bcrypt_hash: str = _pwd_context.hash(_prepare_for_bcrypt(plain_password))
    fernet = _get_fernet()
    encrypted: bytes = fernet.encrypt(bcrypt_hash.encode())
    return encrypted.decode()


def verify_password(plain_password: str, stored_value: str) -> bool:
    """
    Reverse the two layers to verify a password.
    """
    try:
        fernet = _get_fernet()
        bcrypt_hash: str = fernet.decrypt(stored_value.encode()).decode()
        return _pwd_context.verify(_prepare_for_bcrypt(plain_password), bcrypt_hash)
    except (InvalidToken, Exception):
        return False


def change_password(
    current_plain: str,
    new_plain: str,
    stored_value: str,
) -> str:
    """
    Verify current, then produce new two-layer protected value.
    """
    if not verify_password(current_plain, stored_value):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    if current_plain == new_plain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password",
        )

    _validate_password_strength(new_plain)
    return hash_and_encrypt_password(new_plain)


def _validate_password_strength(password: str) -> None:
    """
    Shared password strength rules.
    """
    errors = []
    if len(password) < 8:
        errors.append("at least 8 characters")
    if not any(c.isdigit() for c in password):
        errors.append("at least one number")
    if not any(c.isupper() for c in password):
        errors.append("at least one uppercase letter")
    if not any(c.islower() for c in password):
        errors.append("at least one lowercase letter")

    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Password must contain: {', '.join(errors)}",
        )


# ── JWT operations ──────────────────────────────────────────────────────────


def create_access_token(user_id: str) -> str:
    """
    Create a signed JWT containing the user's UUID.
    """
    secret_key = settings.SECRET_KEY
    algorithm = settings.ALGORITHM
    expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_token(token: str) -> str:
    """
    Decode and validate a JWT.
    """
    secret_key = settings.SECRET_KEY
    algorithm = settings.ALGORITHM

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    except JWTError:
        raise JWTError("Token is invalid or has expired")

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise JWTError("Token is missing subject claim (user_id)")

    return user_id
