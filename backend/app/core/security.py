"""
core/security.py
----------------
Two-layer password security + JWT token operations.

PASSWORD STORAGE STRATEGY (two layers):
  Layer 1 — bcrypt hashing  : one-way, can never be reversed
  Layer 2 — Fernet encryption: the bcrypt hash is then encrypted with
            a symmetric key (ENCRYPTION_KEY from .env) before being
            stored in the database.

  This means even if the database is fully leaked, attackers get only
  encrypted blobs — they cannot even begin brute-forcing bcrypt hashes
  without first obtaining your ENCRYPTION_KEY.

CHANGE PASSWORD:
  change_password() verifies the old password, then produces a fresh
  two-layer protected value for the new password.

JWT:
  create_access_token() / decode_token() for stateless auth.

Depends on: config.py (Dev 1) for secrets. Falls back to env vars
            so you can develop/test before config.py is ready.
"""

from __future__ import annotations

import hashlib
import os
from datetime import datetime, timedelta, timezone

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

# ── bcrypt context ──────────────────────────────────────────────────────────

# bcrypt cost factor 12 — strong, ~300ms per hash (good balance)
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _prepare_for_bcrypt(plain_password: str) -> str:
    """
    Pre-hash with SHA-256 before bcrypt.

    WHY: bcrypt silently truncates (or errors on) passwords over 72 bytes.
    FIX: SHA-256 output is always 64 hex chars (32 bytes) -- safely under
         the limit for any password length.

    SHA-256 alone is not safe for passwords (too fast), but here it is
    only a pre-processing step. bcrypt still does the real slow hashing
    on top. Same approach used by Django, 1Password, and others.
    """
    return hashlib.sha256(plain_password.encode("utf-8")).hexdigest()


# ── Settings helper ─────────────────────────────────────────────────────────


def _get_settings() -> tuple[str, str, int, str]:
    """
    Returns (SECRET_KEY, ALGORITHM, TOKEN_EXPIRE_MINUTES, ENCRYPTION_KEY).
    Tries pydantic settings first, falls back to env vars for standalone dev.
    """
    try:
        from backend.core.config import settings

        return (
            settings.SECRET_KEY,
            settings.ALGORITHM,
            settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            settings.ENCRYPTION_KEY,
        )
    except (ImportError, AttributeError):
        return (
            os.getenv("SECRET_KEY", "dev-secret-key-change-in-production-min-32-chars"),
            os.getenv("ALGORITHM", "HS256"),
            int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")),
            os.getenv("ENCRYPTION_KEY", ""),  # empty triggers auto-generate in dev
        )


def _get_fernet() -> Fernet:
    """
    Build a Fernet cipher from ENCRYPTION_KEY.

    ENCRYPTION_KEY must be a 32-byte URL-safe base64 string.
    Generate one with:  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

    In development, if no key is set, a random one is generated per process
    start (passwords won't survive restarts — fine for dev, never for prod).
    """
    _, _, _, enc_key = _get_settings()

    if not enc_key:
        # Dev-only fallback — warn loudly
        import warnings

        warnings.warn(
            "ENCRYPTION_KEY is not set! Using a random key. "
            "Passwords will NOT survive server restarts. "
            "Set ENCRYPTION_KEY in your .env for persistent storage.",
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
    Layer 1: Hash with bcrypt  →  irreversible, salted
    Layer 2: Encrypt the hash with Fernet  →  stored blob in DB

    Returns a string safe to store in hashed_password column.
    Never store the plain_password anywhere.

    Used in: api/auth.py  register route
             api/auth.py  change_password route
    """
    # Layer 1: SHA-256 pre-hash then bcrypt (fixes 72-byte limit)
    bcrypt_hash: str = _pwd_context.hash(_prepare_for_bcrypt(plain_password))

    # Layer 2: Fernet-encrypt the bcrypt hash
    fernet = _get_fernet()
    encrypted: bytes = fernet.encrypt(bcrypt_hash.encode())

    # Return as a plain string for DB storage (base64-encoded ciphertext)
    return encrypted.decode()


def verify_password(plain_password: str, stored_value: str) -> bool:
    """
    Reverse the two layers to verify a password:
      Step 1 — Fernet-decrypt the stored value  →  get bcrypt hash back
      Step 2 — bcrypt-verify the plain password against that hash

    Returns True if password matches, False otherwise.
    Never raises — authentication errors are handled by callers.

    Used in: api/auth.py  login route
             api/auth.py  change_password route (verify old password)
    """
    try:
        fernet = _get_fernet()
        # Step 1: decrypt to get the original bcrypt hash
        bcrypt_hash: str = fernet.decrypt(stored_value.encode()).decode()
        # Step 2: bcrypt comparison (constant-time, same pre-hash)
        return _pwd_context.verify(_prepare_for_bcrypt(plain_password), bcrypt_hash)
    except (InvalidToken, Exception):
        # Invalid token = tampered/wrong key. Treat as wrong password.
        return False


def change_password(
    current_plain: str,
    new_plain: str,
    stored_value: str,
) -> str:
    """
    Verify the current password, then produce a new two-layer protected
    value for the new password.

    Args:
        current_plain : the password the user typed as "current password"
        new_plain     : the new password the user wants to set
        stored_value  : the existing hashed_password from the DB

    Returns:
        New encrypted value to store in hashed_password column.

    Raises:
        HTTPException 401  if current_plain is wrong
        HTTPException 400  if new_plain is the same as current_plain
        HTTPException 422  if new_plain fails strength validation

    Used in: api/auth.py  POST /api/auth/change-password
    """
    # Verify current password first
    if not verify_password(current_plain, stored_value):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    # Prevent setting the same password
    if current_plain == new_plain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password",
        )

    # Validate new password strength
    _validate_password_strength(new_plain)

    # Generate fresh two-layer protection for the new password
    return hash_and_encrypt_password(new_plain)


def _validate_password_strength(password: str) -> None:
    """
    Shared password strength rules used by both registration and
    change-password flows.

    Raises HTTPException 422 on failure.
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

    Payload claims:
        sub  → user_id (UUID as string)
        exp  → expiry  (now + ACCESS_TOKEN_EXPIRE_MINUTES)
        iat  → issued-at

    Used in: api/auth.py  login + change_password (re-issue token)
    """
    secret_key, algorithm, expire_minutes, _ = _get_settings()

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

    Returns: user_id string (the 'sub' claim)
    Raises:  JWTError if invalid, expired, or tampered.

    Used in: core/dependencies.py → get_current_user
    """
    secret_key, algorithm, _, _ = _get_settings()

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    except JWTError:
        raise JWTError("Token is invalid or has expired")

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise JWTError("Token is missing subject claim (user_id)")

    return user_id
