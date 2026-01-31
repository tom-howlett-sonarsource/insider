"""Tests for database persistence - TDD: write tests first."""
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.db_models import InsightDB
from app.db_repository import InsightDBRepository
from app.models import Insight, Source

# Test constants
TEST_INSIGHT_TITLE = "Test insight"
TEST_DESCRIPTION = "Test description"


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
    """Create a repository with test session."""
    return InsightDBRepository(session)


class TestInsightDBModel:
    """Tests for the InsightDB SQLAlchemy model."""

    def test_create_insight_db(self, session):
        """Can create an InsightDB record."""
        insight = InsightDB(
            id=uuid.uuid4(),
            author_id=uuid.uuid4(),
            title=TEST_INSIGHT_TITLE,
            description=TEST_DESCRIPTION,
            source="conference",
        )
        session.add(insight)
        session.commit()

        assert insight.id is not None
        assert insight.created_at is not None
        assert insight.updated_at is not None

    def test_insight_db_to_domain(self, session):
        """Can convert InsightDB to domain Insight."""
        insight_id = uuid.uuid4()
        author_id = uuid.uuid4()

        db_insight = InsightDB(
            id=insight_id,
            author_id=author_id,
            title=TEST_INSIGHT_TITLE,
            description=TEST_DESCRIPTION,
            source="conference",
        )
        session.add(db_insight)
        session.commit()
        session.refresh(db_insight)

        domain_insight = db_insight.to_domain()

        assert isinstance(domain_insight, Insight)
        assert domain_insight.id == insight_id
        assert domain_insight.title == TEST_INSIGHT_TITLE
        assert domain_insight.source == Source.CONFERENCE


class TestInsightDBRepository:
    """Tests for the database repository."""

    def test_create_insight(self, repository):
        """Can create an insight in the database."""
        insight = Insight(
            title="Users want dark mode",
            description="Feedback from conference.",
            author_id=uuid.uuid4(),
            source=Source.CONFERENCE,
        )

        created = repository.create(insight)

        assert created.id == insight.id
        assert created.title == "Users want dark mode"

    def test_get_by_id(self, repository):
        """Can retrieve an insight by ID."""
        insight = Insight(
            title=TEST_INSIGHT_TITLE,
            description=TEST_DESCRIPTION,
            author_id=uuid.uuid4(),
        )
        repository.create(insight)

        found = repository.get_by_id(insight.id)

        assert found is not None
        assert found.id == insight.id
        assert found.title == TEST_INSIGHT_TITLE

    def test_get_by_id_not_found(self, repository):
        """Returns None when insight not found."""
        fake_id = uuid.uuid4()

        found = repository.get_by_id(fake_id)

        assert found is None

    def test_get_all(self, repository):
        """Can retrieve all insights."""
        for i in range(3):
            insight = Insight(
                title=f"Insight {i}",
                description=f"Description {i}",
                author_id=uuid.uuid4(),
            )
            repository.create(insight)

        insights, total = repository.get_all()

        assert total == 3
        assert len(insights) == 3

    def test_get_all_pagination(self, repository):
        """Pagination works correctly."""
        for i in range(5):
            insight = Insight(
                title=f"Insight {i}",
                description=f"Description {i}",
                author_id=uuid.uuid4(),
            )
            repository.create(insight)

        insights, total = repository.get_all(limit=2, offset=0)

        assert total == 5
        assert len(insights) == 2

    def test_get_all_ordered_by_created_at(self, repository):
        """Insights are returned most recent first."""
        insight1 = Insight(
            title="First",
            description="Created first",
            author_id=uuid.uuid4(),
        )
        repository.create(insight1)

        insight2 = Insight(
            title="Second",
            description="Created second",
            author_id=uuid.uuid4(),
        )
        repository.create(insight2)

        insights, _ = repository.get_all()

        # Most recent first
        assert insights[0].title == "Second"
        assert insights[1].title == "First"

    def test_update_insight(self, repository):
        """Can update an insight."""
        insight = Insight(
            title="Original title",
            description="Original description",
            author_id=uuid.uuid4(),
        )
        repository.create(insight)

        updated = repository.update(insight.id, title="Updated title")

        assert updated is not None
        assert updated.title == "Updated title"
        assert updated.description == "Original description"

    def test_update_insight_not_found(self, repository):
        """Returns None when updating non-existent insight."""
        fake_id = uuid.uuid4()

        updated = repository.update(fake_id, title="New title")

        assert updated is None

    def test_delete_insight(self, repository):
        """Can delete an insight."""
        insight = Insight(
            title="To be deleted",
            description="Will be deleted",
            author_id=uuid.uuid4(),
        )
        repository.create(insight)

        deleted = repository.delete(insight.id)

        assert deleted is True
        assert repository.get_by_id(insight.id) is None

    def test_delete_insight_not_found(self, repository):
        """Returns False when deleting non-existent insight."""
        fake_id = uuid.uuid4()

        deleted = repository.delete(fake_id)

        assert deleted is False
