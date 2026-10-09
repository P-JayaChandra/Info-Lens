import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
import jwt

from app.core.config import get_settings
from app.core.exceptions import (
    AuthenticationException,
    InvalidTokenException,
    TokenExpiredException,
)

settings = get_settings()


def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt with configured salt rounds."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=settings.PASSWORD_HASH_ROUNDS)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a stored bcrypt hash."""
    try:
        plain_bytes = plain_password.encode("utf-8")
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(plain_bytes, hash_bytes)
    except Exception:
        return False


def create_jwt_token(
    subject: str,
    token_type: str = "access",
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a signed JWT token with expiry, subject, type, and standard claims."""
    now = datetime.now(timezone.utc)
    if expires_delta is not None:
        expire = now + expires_delta
    elif token_type == "access":
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    elif token_type == "refresh":
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    else:
        expire = now + timedelta(minutes=15)

    payload: Dict[str, Any] = {
        "sub": str(subject),
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": str(uuid.uuid4()),
        "iss": settings.APP_NAME,
    }

    if extra_claims:
        for k, v in extra_claims.items():
            if k not in payload:
                payload[k] = v

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return token


def create_access_token(
    user_id: str,
    email: Optional[str] = None,
    role: Optional[str] = None,
    organization_id: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Helper to generate standard user access token."""
    claims: Dict[str, Any] = {}
    if email:
        claims["email"] = email
    if role:
        claims["role"] = role
    if organization_id:
        claims["org_id"] = organization_id

    return create_jwt_token(
        subject=user_id,
        token_type="access",
        expires_delta=expires_delta,
        extra_claims=claims,
    )


def create_refresh_token(
    user_id: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Helper to generate user refresh token."""
    return create_jwt_token(
        subject=user_id,
        token_type="refresh",
        expires_delta=expires_delta,
    )


def decode_jwt_token(token: str) -> Dict[str, Any]:
    """Decode and validate signature and expiry of a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"require": ["sub", "exp", "iat", "type"]},
        )
        return payload
    except jwt.ExpiredSignatureError as e:
        raise TokenExpiredException("Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise InvalidTokenException(f"Invalid token: {str(e)}") from e


def verify_jwt_token(token: str, expected_type: str = "access") -> Dict[str, Any]:
    """Verify token validity and assert expected token type."""
    payload = decode_jwt_token(token)
    actual_type = payload.get("type")
    if actual_type != expected_type:
        raise AuthenticationException(
            f"Token type mismatch: expected '{expected_type}', got '{actual_type}'"
        )
    return payload


def generate_secure_random_string(length: int = 32) -> str:
    """Generate a cryptographically secure URL-safe random string."""
    return secrets.token_urlsafe(length)


def generate_api_key(prefix: str = "dkey") -> str:
    """Generate a prefixed random API key."""
    token = secrets.token_hex(24)
    return f"{prefix}_{token}"


def compare_secure_strings(val_a: str, val_b: str) -> bool:
    """Perform constant-time comparison to prevent timing side-channel attacks."""
    return secrets.compare_digest(val_a, val_b)
