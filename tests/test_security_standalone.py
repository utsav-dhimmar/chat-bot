"""
tests/test_security_standalone.py
----------------------------------
Tests for the two-layer password system and change_password().
No database or FastAPI required — runs fully standalone.

Usage:
    uv run python tests/test_security_standalone.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set a real Fernet key so no dev-warning fires during tests
from cryptography.fernet import Fernet
os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
os.environ["SECRET_KEY"]     = "test-secret-key-only-for-unit-tests-abc123"

from backend.core.security import (
    hash_and_encrypt_password,
    verify_password,
    change_password,
    create_access_token,
    decode_token,
)
from fastapi import HTTPException


def check(label: str, passed: bool, detail: str = ""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status}  {label}" + (f"  →  {detail}" if detail else ""))
    return passed


def main():
    print("=" * 60)
    print("  Two-Layer Password Security — Standalone Tests")
    print("=" * 60)

    results = []

    # ── 1. hash_and_encrypt_password ─────────────────────────
    print("\n[1] hash_and_encrypt_password()")

    stored = hash_and_encrypt_password("SecurePass1")

    results.append(check(
        "Stored value is a string",
        isinstance(stored, str),
    ))
    results.append(check(
        "Stored value is NOT the plain password",
        stored != "SecurePass1",
    ))
    results.append(check(
        "Stored value is NOT a raw bcrypt hash (it's encrypted)",
        not stored.startswith("$2b$"),
        f"starts with: {stored[:10]}",
    ))
    results.append(check(
        "Two calls produce DIFFERENT ciphertexts (Fernet uses random IV)",
        hash_and_encrypt_password("SecurePass1") != stored,
    ))

    # ── BCRYPT 72-BYTE FIX ──────────────────────────────────
    print("\n[1b] 72-byte password limit fix")

    long_pw = "A1" + "x" * 100   # 102 chars — would crash old code
    try:
        stored_long = hash_and_encrypt_password(long_pw)
        results.append(check(
            "Password > 72 bytes hashes without error",
            isinstance(stored_long, str),
        ))
        results.append(check(
            "Password > 72 bytes verifies correctly",
            verify_password(long_pw, stored_long) is True,
        ))
        results.append(check(
            "Different long passwords do NOT match each other",
            verify_password("A1" + "y" * 100, stored_long) is False,
        ))
    except Exception as e:
        results.append(check("Long password should not raise", False, str(e)))
        results.append(check("Skipped", False))
        results.append(check("Skipped", False))

    # ── 2. verify_password ──────────────────────────────────
    print("\n[2] verify_password()")

    results.append(check(
        "Correct password returns True",
        verify_password("SecurePass1", stored) is True,
    ))
    results.append(check(
        "Wrong password returns False",
        verify_password("WrongPass99", stored) is False,
    ))
    results.append(check(
        "Empty string returns False",
        verify_password("", stored) is False,
    ))
    results.append(check(
        "Tampered stored value returns False (no crash)",
        verify_password("SecurePass1", "corrupted-garbage-value") is False,
    ))

    # ── 3. change_password ──────────────────────────────────
    print("\n[3] change_password()")

    stored_v1 = hash_and_encrypt_password("OldPass1")

    # Successful change
    try:
        stored_v2 = change_password("OldPass1", "NewPass2", stored_v1)
        results.append(check(
            "Valid change returns new stored value",
            isinstance(stored_v2, str) and stored_v2 != stored_v1,
        ))
        results.append(check(
            "New password verifies correctly with new stored value",
            verify_password("NewPass2", stored_v2) is True,
        ))
        results.append(check(
            "Old password no longer works on new stored value",
            verify_password("OldPass1", stored_v2) is False,
        ))
    except Exception as e:
        results.append(check("Valid change should not raise", False, str(e)))
        results.append(check("Skipped (previous failed)", False))
        results.append(check("Skipped (previous failed)", False))

    # Wrong current password
    try:
        change_password("WrongOldPass", "NewPass2", stored_v1)
        results.append(check("Wrong current password → should raise 401", False))
    except HTTPException as e:
        results.append(check(
            "Wrong current password raises HTTP 401",
            e.status_code == 401,
            e.detail,
        ))

    # Same password
    try:
        change_password("OldPass1", "OldPass1", stored_v1)
        results.append(check("Same new password → should raise 400", False))
    except HTTPException as e:
        results.append(check(
            "Same new password raises HTTP 400",
            e.status_code == 400,
            e.detail,
        ))

    # Weak new password (no uppercase)
    try:
        change_password("OldPass1", "weakpass1", stored_v1)
        results.append(check("Weak new password → should raise 422", False))
    except HTTPException as e:
        results.append(check(
            "Weak new password raises HTTP 422",
            e.status_code == 422,
            e.detail,
        ))

    # ── 4. JWT round-trip ───────────────────────────────────
    print("\n[4] JWT round-trip")

    token = create_access_token("user-uuid-1234")
    results.append(check(
        "create_access_token returns a string",
        isinstance(token, str) and len(token) > 20,
    ))

    decoded = decode_token(token)
    results.append(check(
        "decode_token returns correct user_id",
        decoded == "user-uuid-1234",
        f"got: {decoded}",
    ))

    try:
        decode_token("totally.invalid.token")
        results.append(check("Invalid token → should raise JWTError", False))
    except Exception:
        results.append(check("Invalid token raises exception", True))

    # ── Summary ─────────────────────────────────────────────
    passed = sum(results)
    total  = len(results)
    print("\n" + "=" * 60)
    print(f"  Results: {passed}/{total} tests passed")
    if passed == total:
        print("  🎉 All security tests passed!")
        print("  Two-layer encryption + change_password is working correctly.")
    else:
        print(f"  ⚠️  {total - passed} test(s) failed — review output above.")
    print("=" * 60)


if __name__ == "__main__":
    main()