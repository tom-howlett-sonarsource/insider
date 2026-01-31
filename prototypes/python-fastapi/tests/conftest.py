"""Shared test fixtures."""
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.db_models import UserDB
from app.main import app
from app.security import create_access_token, get_password_hash

# Test user constants
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_USER_NAME = "Test User"


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def session(engine):
    """Create a database session for testing."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def client(engine):
    """Create a test client for the API with test database."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(engine):
    """Create a test user in the database and return user info."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as session:
        user_id = uuid.uuid4()
        user = UserDB(
            id=user_id,
            email=TEST_USER_EMAIL,
            name=TEST_USER_NAME,
            hashed_password=get_password_hash(TEST_USER_PASSWORD),
            role="advocate",
        )
        session.add(user)
        session.commit()
        yield {
            "id": user_id,
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME,
        }


@pytest.fixture
def auth_headers(test_user):
    """Get auth headers with valid JWT token."""
    token = create_access_token(data={"sub": test_user["email"]})
    return {"Authorization": f"Bearer {token}"}
