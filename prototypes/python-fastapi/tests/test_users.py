"""Tests for user endpoints - TDD: write tests first."""
import pytest

# Test constants
USERS_ME_ENDPOINT = "/api/v1/users/me"


class TestGetCurrentUser:
    """Tests for GET /api/v1/users/me."""

    @pytest.mark.anyio
    async def test_get_me_authenticated(self, client, auth_headers, test_user):
        """Returns current user data with valid token."""
        response = await client.get(USERS_ME_ENDPOINT, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["email"]
        assert data["name"] == test_user["name"]
        assert "id" in data
        assert "role" in data
        # Password should never be returned
        assert "password" not in data
        assert "hashed_password" not in data

    @pytest.mark.anyio
    async def test_get_me_without_token_returns_401(self, client):
        """Returns 401 without token."""
        response = await client.get(USERS_ME_ENDPOINT)

        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_get_me_invalid_token_returns_401(self, client):
        """Returns 401 with invalid token."""
        response = await client.get(
            USERS_ME_ENDPOINT,
            headers={"Authorization": "Bearer invalid.token.here"},
        )

        assert response.status_code == 401
