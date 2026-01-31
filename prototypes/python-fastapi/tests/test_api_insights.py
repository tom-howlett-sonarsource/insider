"""Tests for the insights API endpoints - TDD: write tests first."""
import uuid

import pytest

# Test constants
INSIGHTS_ENDPOINT = "/api/v1/insights"
TEST_INSIGHT_TITLE = "Test insight"
TEST_DESCRIPTION = "Test description"
SOME_DESCRIPTION = "Some description"


class TestListInsights:
    """Tests for GET /api/v1/insights."""

    @pytest.mark.anyio
    async def test_list_insights_empty(self, client):
        """Returns empty list when no insights exist."""
        response = await client.get(INSIGHTS_ENDPOINT)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.anyio
    async def test_list_insights_returns_insights(self, client):
        """Returns list of insights."""
        # First create an insight
        await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": TEST_INSIGHT_TITLE,
                "description": TEST_DESCRIPTION,
            },
        )

        response = await client.get(INSIGHTS_ENDPOINT)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == TEST_INSIGHT_TITLE


class TestCreateInsight:
    """Tests for POST /api/v1/insights."""

    @pytest.mark.anyio
    async def test_create_insight_minimal(self, client):
        """Can create insight with just title and description."""
        response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": "Users want dark mode",
                "description": "Feedback from conference.",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Users want dark mode"
        assert data["description"] == "Feedback from conference."
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.anyio
    async def test_create_insight_with_source(self, client):
        """Can create insight with source."""
        response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": "API docs are confusing",
                "description": "Multiple users mentioned this.",
                "source": "community_forum",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["source"] == "community_forum"

    @pytest.mark.anyio
    async def test_create_insight_missing_title(self, client):
        """Returns 400 when title is missing."""
        response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "description": SOME_DESCRIPTION,
            },
        )

        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_create_insight_empty_title(self, client):
        """Returns 400 when title is empty."""
        response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": "",
                "description": SOME_DESCRIPTION,
            },
        )

        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_create_insight_title_too_long(self, client):
        """Returns 400 when title exceeds 200 characters."""
        response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": "x" * 201,
                "description": SOME_DESCRIPTION,
            },
        )

        assert response.status_code == 422


class TestGetInsight:
    """Tests for GET /api/v1/insights/{id}."""

    @pytest.mark.anyio
    async def test_get_insight(self, client):
        """Can retrieve an insight by ID."""
        # First create an insight
        create_response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": TEST_INSIGHT_TITLE,
                "description": TEST_DESCRIPTION,
            },
        )
        insight_id = create_response.json()["id"]

        response = await client.get(f"{INSIGHTS_ENDPOINT}/{insight_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == insight_id
        assert data["title"] == TEST_INSIGHT_TITLE

    @pytest.mark.anyio
    async def test_get_insight_not_found(self, client):
        """Returns 404 when insight doesn't exist."""
        fake_id = str(uuid.uuid4())

        response = await client.get(f"{INSIGHTS_ENDPOINT}/{fake_id}")

        assert response.status_code == 404


class TestUpdateInsight:
    """Tests for PUT /api/v1/insights/{id}."""

    @pytest.mark.anyio
    async def test_update_insight(self, client):
        """Can update an insight."""
        # First create an insight
        create_response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": "Original title",
                "description": "Original description",
            },
        )
        insight_id = create_response.json()["id"]

        response = await client.put(
            f"{INSIGHTS_ENDPOINT}/{insight_id}",
            json={
                "title": "Updated title",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated title"
        assert data["description"] == "Original description"

    @pytest.mark.anyio
    async def test_update_insight_not_found(self, client):
        """Returns 404 when insight doesn't exist."""
        fake_id = str(uuid.uuid4())

        response = await client.put(
            f"{INSIGHTS_ENDPOINT}/{fake_id}",
            json={"title": "Updated"},
        )

        assert response.status_code == 404


class TestDeleteInsight:
    """Tests for DELETE /api/v1/insights/{id}."""

    @pytest.mark.anyio
    async def test_delete_insight(self, client):
        """Can delete an insight."""
        # First create an insight
        create_response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": "To be deleted",
                "description": "This will be deleted",
            },
        )
        insight_id = create_response.json()["id"]

        response = await client.delete(f"{INSIGHTS_ENDPOINT}/{insight_id}")

        assert response.status_code == 204

        # Verify it's gone
        get_response = await client.get(f"{INSIGHTS_ENDPOINT}/{insight_id}")
        assert get_response.status_code == 404

    @pytest.mark.anyio
    async def test_delete_insight_not_found(self, client):
        """Returns 404 when insight doesn't exist."""
        fake_id = str(uuid.uuid4())

        response = await client.delete(f"{INSIGHTS_ENDPOINT}/{fake_id}")

        assert response.status_code == 404
