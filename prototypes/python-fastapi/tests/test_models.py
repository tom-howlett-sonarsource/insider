"""Tests for data models - TDD: write tests first, then implement."""
import uuid
from datetime import datetime

import pytest


class TestInsightModel:
    """Tests for the Insight model."""

    def test_create_insight_with_required_fields(self):
        """An insight can be created with just title and description."""
        from app.models import Insight

        insight = Insight(
            title="Users want dark mode",
            description="Multiple users at the conference asked about dark mode support.",
            author_id=uuid.uuid4(),
        )

        assert insight.title == "Users want dark mode"
        assert insight.description == "Multiple users at the conference asked about dark mode support."
        assert insight.id is not None
        assert insight.created_at is not None
        assert insight.updated_at is not None

    def test_create_insight_with_source(self):
        """An insight can have a source."""
        from app.models import Insight, Source

        insight = Insight(
            title="API documentation is confusing",
            description="Feedback from Discord channel.",
            author_id=uuid.uuid4(),
            source=Source.COMMUNITY_FORUM,
        )

        assert insight.source == Source.COMMUNITY_FORUM

    def test_insight_source_enum_values(self):
        """Source enum has the expected values."""
        from app.models import Source

        assert Source.COMMUNITY_FORUM.value == "community_forum"
        assert Source.CONFERENCE.value == "conference"
        assert Source.SOCIAL_MEDIA.value == "social_media"
        assert Source.MEETUP.value == "meetup"
        assert Source.OTHER.value == "other"

    def test_insight_title_max_length(self):
        """Insight title should not exceed 200 characters."""
        from app.models import Insight

        long_title = "x" * 201

        with pytest.raises(ValueError):
            Insight(
                title=long_title,
                description="Description",
                author_id=uuid.uuid4(),
            )

    def test_insight_title_required(self):
        """Insight must have a title."""
        from app.models import Insight

        with pytest.raises(ValueError):
            Insight(
                title="",
                description="Description",
                author_id=uuid.uuid4(),
            )

    def test_insight_description_required(self):
        """Insight must have a description."""
        from app.models import Insight

        with pytest.raises(ValueError):
            Insight(
                title="Title",
                description="",
                author_id=uuid.uuid4(),
            )


class TestProductModel:
    """Tests for the Product model."""

    def test_create_product(self):
        """A product can be created with a name."""
        from app.models import Product

        product = Product(name="SonarQube")

        assert product.name == "SonarQube"
        assert product.id is not None
        assert product.description is None

    def test_create_product_with_description(self):
        """A product can have an optional description."""
        from app.models import Product

        product = Product(
            name="SonarLint",
            description="IDE extension for code quality",
        )

        assert product.description == "IDE extension for code quality"

    def test_product_name_required(self):
        """Product must have a name."""
        from app.models import Product

        with pytest.raises(ValueError):
            Product(name="")


class TestTagModel:
    """Tests for the Tag model."""

    def test_create_tag(self):
        """A tag can be created with a name."""
        from app.models import Tag

        tag = Tag(name="ux")

        assert tag.name == "ux"
        assert tag.id is not None

    def test_tag_name_lowercase(self):
        """Tag names are stored as lowercase."""
        from app.models import Tag

        tag = Tag(name="UX")

        assert tag.name == "ux"

    def test_tag_name_required(self):
        """Tag must have a name."""
        from app.models import Tag

        with pytest.raises(ValueError):
            Tag(name="")


class TestUserModel:
    """Tests for the User model."""

    def test_create_user(self):
        """A user can be created with email, name, and role."""
        from app.models import User, Role

        user = User(
            email="tom@example.com",
            name="Tom",
            role=Role.ADVOCATE,
        )

        assert user.email == "tom@example.com"
        assert user.name == "Tom"
        assert user.role == Role.ADVOCATE
        assert user.id is not None

    def test_role_enum_values(self):
        """Role enum has the expected values."""
        from app.models import Role

        assert Role.ADVOCATE.value == "advocate"
        assert Role.PRODUCT_MANAGER.value == "product_manager"

    def test_user_email_required(self):
        """User must have an email."""
        from app.models import User, Role

        with pytest.raises(ValueError):
            User(email="", name="Tom", role=Role.ADVOCATE)
