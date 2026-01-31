"""Tests for authentication endpoints - TDD: write tests first."""
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.db_models import UserDB
from app.main import app
from app.security import get_password_hash

# Test constants
AUTH_ENDPOINT = "/api/v1/auth/login"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"
TEST_NAME = "Test User"


@pytest.fixture
def test_user(engine):
    """Create a test user in the database."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    with TestingSessionLocal() as session:
        user = UserDB(
            id=uuid.uuid4(),
            email=TEST_EMAIL,
            name=TEST_NAME,
            hashed_password=get_password_hash(TEST_PASSWORD),
            role="advocate",
        )
        session.add(user)
        session.commit()
        yield user


class TestLogin:
    """Tests for POST /api/v1/auth/login."""

    @pytest.mark.anyio
    async def test_login_success(self, client, test_user):
        """Returns JWT token for valid credentials."""
        response = await client.post(
            AUTH_ENDPOINT,
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        # JWT has 3 parts
        assert len(data["access_token"].split(".")) == 3

    @pytest.mark.anyio
    async def test_login_wrong_password(self, client, test_user):
        """Returns 401 for incorrect password."""
        response = await client.post(
            AUTH_ENDPOINT,
            json={
                "email": TEST_EMAIL,
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.anyio
    async def test_login_user_not_found(self, client):
        """Returns 401 for non-existent email."""
        response = await client.post(
            AUTH_ENDPOINT,
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword",
            },
        )

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.anyio
    async def test_login_missing_email(self, client):
        """Returns 422 for missing email."""
        response = await client.post(
            AUTH_ENDPOINT,
            json={
                "password": TEST_PASSWORD,
            },
        )

        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_login_missing_password(self, client):
        """Returns 422 for missing password."""
        response = await client.post(
            AUTH_ENDPOINT,
            json={
                "email": TEST_EMAIL,
            },
        )

        assert response.status_code == 422
