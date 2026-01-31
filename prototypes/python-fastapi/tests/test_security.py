"""Tests for security utilities - TDD: write tests first."""
from datetime import timedelta

import pytest
from jose import jwt

from app.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    decode_token,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    """Tests for password hashing utilities."""

    def test_password_hash_is_not_plaintext(self):
        """Hashed password should not equal plaintext."""
        password = "mysecretpassword"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > len(password)

    def test_verify_password_correct(self):
        """verify_password returns True for correct password."""
        password = "mysecretpassword"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """verify_password returns False for incorrect password."""
        password = "mysecretpassword"
        hashed = get_password_hash(password)

        assert verify_password("wrongpassword", hashed) is False

    def test_same_password_different_hashes(self):
        """Same password should produce different hashes (salting)."""
        password = "mysecretpassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        # Both should still verify
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Tests for JWT token utilities."""

    def test_create_access_token_returns_string(self):
        """create_access_token returns a JWT string."""
        token = create_access_token(data={"sub": "test@example.com"})

        assert isinstance(token, str)
        assert len(token) > 0
        # JWT has 3 parts separated by dots
        assert len(token.split(".")) == 3

    def test_decode_token_valid(self):
        """decode_token returns payload for valid token."""
        email = "test@example.com"
        token = create_access_token(data={"sub": email})

        payload = decode_token(token)

        assert payload["sub"] == email
        assert "exp" in payload

    def test_decode_token_with_custom_expiry(self):
        """Token with custom expiry is valid."""
        token = create_access_token(
            data={"sub": "test@example.com"},
            expires_delta=timedelta(hours=1),
        )

        payload = decode_token(token)
        assert payload["sub"] == "test@example.com"

    def test_decode_token_invalid(self):
        """decode_token raises for malformed token."""
        with pytest.raises(Exception):
            decode_token("invalid.token.here")

    def test_decode_token_wrong_signature(self):
        """decode_token raises for token with wrong signature."""
        # Create a token with a different secret
        bad_token = jwt.encode(
            {"sub": "test@example.com"},
            "wrong-secret-key",
            algorithm=ALGORITHM,
        )

        with pytest.raises(Exception):
            decode_token(bad_token)

    def test_token_contains_expiration(self):
        """Token payload includes expiration claim."""
        token = create_access_token(data={"sub": "test@example.com"})

        # Decode without verification to check claims
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert "exp" in payload
