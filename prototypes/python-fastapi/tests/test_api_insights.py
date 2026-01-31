"""Tests for the insights API endpoints - TDD: write tests first."""
import uuid

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """Create a test client for the API."""
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


class TestListInsights:
    """Tests for GET /api/v1/insights."""

    @pytest.mark.anyio
    async def test_list_insights_empty(self, client):
        """Returns empty list when no insights exist."""
        response = await client.get("/api/v1/insights")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.anyio
    async def test_list_insights_returns_insights(self, client):
        """Returns list of insights."""
        # First create an insight
        await client.post(
            "/api/v1/insights",
            json={
                "title": "Test insight",
                "description": "Test description",
            },
        )

        response = await client.get("/api/v1/insights")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Test insight"


class TestCreateInsight:
    """Tests for POST /api/v1/insights."""

    @pytest.mark.anyio
    async def test_create_insight_minimal(self, client):
        """Can create insight with just title and description."""
        response = await client.post(
            "/api/v1/insights",
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
            "/api/v1/insights",
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
            "/api/v1/insights",
            json={
                "description": "Some description",
            },
        )

        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_create_insight_empty_title(self, client):
        """Returns 400 when title is empty."""
        response = await client.post(
            "/api/v1/insights",
            json={
                "title": "",
                "description": "Some description",
            },
        )

        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_create_insight_title_too_long(self, client):
        """Returns 400 when title exceeds 200 characters."""
        response = await client.post(
            "/api/v1/insights",
            json={
                "title": "x" * 201,
                "description": "Some description",
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
            "/api/v1/insights",
            json={
                "title": "Test insight",
                "description": "Test description",
            },
        )
        insight_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/insights/{insight_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == insight_id
        assert data["title"] == "Test insight"

    @pytest.mark.anyio
    async def test_get_insight_not_found(self, client):
        """Returns 404 when insight doesn't exist."""
        fake_id = str(uuid.uuid4())

        response = await client.get(f"/api/v1/insights/{fake_id}")

        assert response.status_code == 404


class TestUpdateInsight:
    """Tests for PUT /api/v1/insights/{id}."""

    @pytest.mark.anyio
    async def test_update_insight(self, client):
        """Can update an insight."""
        # First create an insight
        create_response = await client.post(
            "/api/v1/insights",
            json={
                "title": "Original title",
                "description": "Original description",
            },
        )
        insight_id = create_response.json()["id"]

        response = await client.put(
            f"/api/v1/insights/{insight_id}",
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
            f"/api/v1/insights/{fake_id}",
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
            "/api/v1/insights",
            json={
                "title": "To be deleted",
                "description": "This will be deleted",
            },
        )
        insight_id = create_response.json()["id"]

        response = await client.delete(f"/api/v1/insights/{insight_id}")

        assert response.status_code == 204

        # Verify it's gone
        get_response = await client.get(f"/api/v1/insights/{insight_id}")
        assert get_response.status_code == 404

    @pytest.mark.anyio
    async def test_delete_insight_not_found(self, client):
        """Returns 404 when insight doesn't exist."""
        fake_id = str(uuid.uuid4())

        response = await client.delete(f"/api/v1/insights/{fake_id}")

        assert response.status_code == 404
