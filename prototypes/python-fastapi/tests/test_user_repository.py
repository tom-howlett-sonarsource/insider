"""Tests for user repository - TDD: write tests first."""
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.db_models import UserDB
from app.models import Role, User
from app.security import get_password_hash
from app.user_repository import UserDBRepository

# Test constants
TEST_EMAIL = "test@example.com"
TEST_NAME = "Test User"
TEST_PASSWORD = "testpassword123"


@pytest.fixture
def engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def session(engine):
    """Create a database session for testing."""
    with Session(engine) as session:
        yield session


@pytest.fixture
def repository(session):
    """Create a user repository with test session."""
    return UserDBRepository(session)


@pytest.fixture
def test_user_db(session):
    """Create a test user in the database."""
    user = UserDB(
        id=uuid.uuid4(),
        email=TEST_EMAIL,
        name=TEST_NAME,
        hashed_password=get_password_hash(TEST_PASSWORD),
        role="advocate",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


class TestUserDBModel:
    """Tests for the UserDB SQLAlchemy model."""

    def test_create_user_db(self, session):
        """Can create a UserDB record."""
        user = UserDB(
            id=uuid.uuid4(),
            email=TEST_EMAIL,
            name=TEST_NAME,
            hashed_password=get_password_hash(TEST_PASSWORD),
            role="advocate",
        )
        session.add(user)
        session.commit()

        assert user.id is not None
        assert user.created_at is not None

    def test_user_db_to_domain(self, session):
        """Can convert UserDB to domain User."""
        user_id = uuid.uuid4()
        db_user = UserDB(
            id=user_id,
            email=TEST_EMAIL,
            name=TEST_NAME,
            hashed_password=get_password_hash(TEST_PASSWORD),
            role="product_manager",
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        domain_user = db_user.to_domain()

        assert isinstance(domain_user, User)
        assert domain_user.id == user_id
        assert domain_user.email == TEST_EMAIL
        assert domain_user.role == Role.PRODUCT_MANAGER


class TestUserDBRepository:
    """Tests for the user database repository."""

    def test_get_by_email_found(self, repository, test_user_db):
        """Returns user when email exists."""
        user = repository.get_by_email(TEST_EMAIL)

        assert user is not None
        assert user.email == TEST_EMAIL
        assert user.name == TEST_NAME

    def test_get_by_email_not_found(self, repository):
        """Returns None when email doesn't exist."""
        user = repository.get_by_email("nonexistent@example.com")

        assert user is None

    def test_get_by_id_found(self, repository, test_user_db):
        """Returns user when ID exists."""
        user = repository.get_by_id(uuid.UUID(test_user_db.id))

        assert user is not None
        assert user.email == TEST_EMAIL

    def test_get_by_id_not_found(self, repository):
        """Returns None when ID doesn't exist."""
        user = repository.get_by_id(uuid.uuid4())

        assert user is None

    def test_get_by_email_with_password(self, repository, test_user_db):
        """Can get user with hashed password for verification."""
        user, hashed_password = repository.get_by_email_with_password(TEST_EMAIL)

        assert user is not None
        assert hashed_password is not None
        assert len(hashed_password) > 0
