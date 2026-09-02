import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import jwt
from app.core.config import settings

def hash_secret(secret: str) -> str:
    """Deterministic salted SHA256 hash for passwords and OTPs, zero external C-dependencies."""
    salt = settings.SECRET_KEY[:16].encode("utf-8")
    return hmac.new(salt, secret.encode("utf-8"), hashlib.sha256).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    if not plain or not hashed:
        return False
    return hmac.compare_digest(hash_secret(plain), hashed)

def get_password_hash(password: str) -> str:
    return hash_secret(password)

def create_access_token(subject: str | Any, role: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "role": role
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
