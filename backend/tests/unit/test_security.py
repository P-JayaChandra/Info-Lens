from datetime import timedelta
import pytest
from app.core.exceptions import (
    AuthenticationException,
    InvalidTokenException,
    TokenExpiredException,
)
from app.core.security import (
    compare_secure_strings,
    create_access_token,
    create_jwt_token,
    create_refresh_token,
    decode_jwt_token,
    generate_api_key,
    generate_secure_random_string,
    hash_password,
    verify_jwt_token,
    verify_password,
)


def test_password_hashing_and_verification():
    plain = "SuperSecretPassword123!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert hashed.startswith("$2b$")
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_create_and_decode_access_token():
    user_id = "user_12345"
    token = create_access_token(
        user_id=user_id,
        email="test@example.com",
        role="admin",
        organization_id="org_999",
    )
    payload = decode_jwt_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "access"
    assert payload["email"] == "test@example.com"
    assert payload["role"] == "admin"
    assert payload["org_id"] == "org_999"
    assert "exp" in payload
    assert "iat" in payload
    assert "jti" in payload


def test_create_and_decode_refresh_token():
    user_id = "user_ref_99"
    token = create_refresh_token(user_id=user_id)
    payload = decode_jwt_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"


def test_verify_jwt_token_type_check():
    access_token = create_access_token(user_id="u1")
    # Verify correctly as access
    payload = verify_jwt_token(access_token, expected_type="access")
    assert payload["sub"] == "u1"

    # Mismatched expected type should raise AuthenticationException
    with pytest.raises(AuthenticationException) as exc_info:
        verify_jwt_token(access_token, expected_type="refresh")
    assert "Token type mismatch" in str(exc_info.value)


def test_expired_jwt_token():
    expired_token = create_jwt_token(
        subject="user_exp",
        expires_delta=timedelta(seconds=-10),
    )
    with pytest.raises(TokenExpiredException):
        decode_jwt_token(expired_token)


def test_invalid_jwt_token():
    with pytest.raises(InvalidTokenException):
        decode_jwt_token("invalid.token.signature")


def test_secure_random_string_generation():
    token1 = generate_secure_random_string(32)
    token2 = generate_secure_random_string(32)
    assert len(token1) >= 32
    assert token1 != token2


def test_generate_api_key():
    key = generate_api_key(prefix="testkey")
    assert key.startswith("testkey_")
    assert len(key) > 20


def test_compare_secure_strings():
    assert compare_secure_strings("token123", "token123") is True
    assert compare_secure_strings("token123", "token456") is False
