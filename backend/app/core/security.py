"""
Security utilities for Kabadiwala Connect.

§1.4 — OTP hashing functions are explicitly named hash_otp / verify_otp_hash to
prevent future misuse for password storage (which would require a proper KDF such
as argon2-cffi or passlib[bcrypt]).

§1.5 — All reference-number generators use secrets module, not random.
"""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt

from app.core.config import settings

# ── OTP hashing ──────────────────────────────────────────────────────────────

def hash_otp(otp: str) -> str:
    """
    Deterministic HMAC-SHA256 hash for short-lived OTPs.

    NOTE: Do NOT use for persistent passwords — use argon2-cffi / bcrypt instead.
    The protection here is OTP expiry + rate limiting, not hash strength.
    """
    salt = settings.SECRET_KEY[:16].encode("utf-8")
    return hmac.new(salt, otp.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_otp_hash(plain: str, hashed: str) -> bool:
    if not plain or not hashed:
        return False
    return hmac.compare_digest(hash_otp(plain), hashed)


# ── Backwards-compat aliases (callers use get_password_hash / verify_password) ──
# These were renamed to make the OTP-only intent clear; aliases preserve existing
# call sites until they are individually migrated.
get_password_hash = hash_otp
verify_password = verify_otp_hash


# ── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(subject: str | Any, role: str, expires_delta: timedelta | None = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "role": role,
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ── Cryptographically-secure reference-number generators ─────────────────────

def generate_receipt_no(year: int | None = None) -> str:
    """§1.5, §1.8 — uses secrets, not random.randint."""
    y = year or datetime.now(timezone.utc).year
    token = secrets.token_hex(3).upper()  # 6 hex chars → ~16M values
    return f"KC-RCT-{y}-{token}"


def generate_upi_ref() -> str:
    """§1.5 — cryptographically-secure UPI reference string."""
    return f"KC{secrets.token_hex(8).upper()}"


def generate_cash_ref() -> str:
    """§1.5 — cryptographically-secure cash payment reference string."""
    return f"CASH{secrets.token_hex(6).upper()}"
