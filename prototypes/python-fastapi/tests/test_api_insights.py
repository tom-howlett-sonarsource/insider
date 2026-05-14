"""Tests for the insights API endpoints - TDD: write tests first."""
import logging
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest

# Test constants
INSIGHTS_ENDPOINT = "/api/v1/insights"
ANALYTICS_ENDPOINT = "/api/v1/insights/analytics"
EXPORT_ENDPOINT = "/api/v1/insights/export"
TEST_INSIGHT_TITLE = "Test insight"
TEST_DESCRIPTION = "Test description"
SOME_DESCRIPTION = "Some description"
MAIN_LOGGER = "app.main"
WEBHOOK_URL = "https://hooks.example.com/notify"


class TestListInsights:
    """Tests for GET /api/v1/insights."""

    @pytest.mark.anyio
    async def test_list_insights_empty(self, client, auth_headers):
        """Returns empty list when no insights exist."""
        response = await client.get(INSIGHTS_ENDPOINT, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.anyio
    async def test_list_insights_returns_insights(self, client, auth_headers):
        """Returns list of insights."""
        # First create an insight
        await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": TEST_INSIGHT_TITLE,
                "description": TEST_DESCRIPTION,
            },
            headers=auth_headers,
        )

        response = await client.get(INSIGHTS_ENDPOINT, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == TEST_INSIGHT_TITLE

    @pytest.mark.anyio
    async def test_list_insights_without_auth_returns_401(self, client):
        """Returns 401 when no token provided."""
        response = await client.get(INSIGHTS_ENDPOINT)

        assert response.status_code == 401


class TestCreateInsight:
    """Tests for POST /api/v1/insights."""

    @pytest.mark.anyio
    async def test_create_insight_minimal(self, client, auth_headers):
        """Can create insight with just title and description."""
        response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": "Users want dark mode",
                "description": "Feedback from conference.",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Users want dark mode"
        assert data["description"] == "Feedback from conference."
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.anyio
    async def test_create_insight_with_source(self, client, auth_headers):
        """Can create insight with source."""
        response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": "API docs are confusing",
                "description": "Multiple users mentioned this.",
                "source": "community_forum",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["source"] == "community_forum"

    @pytest.mark.anyio
    async def test_create_insight_missing_title(self, client, auth_headers):
        """Returns 422 when title is missing."""
        response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "description": SOME_DESCRIPTION,
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_create_insight_empty_title(self, client, auth_headers):
        """Returns 422 when title is empty."""
        response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": "",
                "description": SOME_DESCRIPTION,
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_create_insight_title_too_long(self, client, auth_headers):
        """Returns 422 when title exceeds 200 characters."""
        response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": "x" * 201,
                "description": SOME_DESCRIPTION,
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_create_insight_without_auth_returns_401(self, client):
        """Returns 401 when no token provided."""
        response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": TEST_INSIGHT_TITLE,
                "description": TEST_DESCRIPTION,
            },
        )

        assert response.status_code == 401


class TestGetInsight:
    """Tests for GET /api/v1/insights/{id}."""

    @pytest.mark.anyio
    async def test_get_insight(self, client, auth_headers):
        """Can retrieve an insight by ID."""
        # First create an insight
        create_response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": TEST_INSIGHT_TITLE,
                "description": TEST_DESCRIPTION,
            },
            headers=auth_headers,
        )
        insight_id = create_response.json()["id"]

        response = await client.get(
            f"{INSIGHTS_ENDPOINT}/{insight_id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == insight_id
        assert data["title"] == TEST_INSIGHT_TITLE

    @pytest.mark.anyio
    async def test_get_insight_not_found(self, client, auth_headers):
        """Returns 404 when insight doesn't exist."""
        fake_id = str(uuid.uuid4())

        response = await client.get(
            f"{INSIGHTS_ENDPOINT}/{fake_id}", headers=auth_headers
        )

        assert response.status_code == 404


class TestUpdateInsight:
    """Tests for PUT /api/v1/insights/{id}."""

    @pytest.mark.anyio
    async def test_update_insight(self, client, auth_headers):
        """Can update an insight."""
        # First create an insight
        create_response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": "Original title",
                "description": "Original description",
            },
            headers=auth_headers,
        )
        insight_id = create_response.json()["id"]

        response = await client.put(
            f"{INSIGHTS_ENDPOINT}/{insight_id}",
            json={
                "title": "Updated title",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated title"
        assert data["description"] == "Original description"

    @pytest.mark.anyio
    async def test_update_insight_not_found(self, client, auth_headers):
        """Returns 404 when insight doesn't exist."""
        fake_id = str(uuid.uuid4())

        response = await client.put(
            f"{INSIGHTS_ENDPOINT}/{fake_id}",
            json={"title": "Updated"},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestDeleteInsight:
    """Tests for DELETE /api/v1/insights/{id}."""

    @pytest.mark.anyio
    async def test_delete_insight(self, client, auth_headers):
        """Can delete an insight."""
        # First create an insight
        create_response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": "To be deleted",
                "description": "This will be deleted",
            },
            headers=auth_headers,
        )
        insight_id = create_response.json()["id"]

        response = await client.delete(
            f"{INSIGHTS_ENDPOINT}/{insight_id}", headers=auth_headers
        )

        assert response.status_code == 204

        # Verify it's gone
        get_response = await client.get(
            f"{INSIGHTS_ENDPOINT}/{insight_id}", headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.anyio
    async def test_delete_insight_not_found(self, client, auth_headers):
        """Returns 404 when insight doesn't exist."""
        fake_id = str(uuid.uuid4())

        response = await client.delete(
            f"{INSIGHTS_ENDPOINT}/{fake_id}", headers=auth_headers
        )

        assert response.status_code == 404


class TestInsightLogging:
    """Tests for insight CRUD operation logging."""

    @pytest.mark.anyio
    async def test_create_insight_logs_info(
        self, client, auth_headers, caplog
    ):
        """Creating an insight logs INFO with insight_id and user_id."""
        with caplog.at_level(logging.INFO, logger=MAIN_LOGGER):
            response = await client.post(
                INSIGHTS_ENDPOINT,
                json={
                    "title": TEST_INSIGHT_TITLE,
                    "description": TEST_DESCRIPTION,
                },
                headers=auth_headers,
            )
        insight_id = response.json()["id"]
        assert any(
            "Insight created" in r.message and insight_id in r.message
            for r in caplog.records
        )

    @pytest.mark.anyio
    async def test_update_insight_logs_info(
        self, client, auth_headers, caplog
    ):
        """Updating an insight logs INFO with insight_id."""
        create_response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": TEST_INSIGHT_TITLE,
                "description": TEST_DESCRIPTION,
            },
            headers=auth_headers,
        )
        insight_id = create_response.json()["id"]

        with caplog.at_level(logging.INFO, logger=MAIN_LOGGER):
            await client.put(
                f"{INSIGHTS_ENDPOINT}/{insight_id}",
                json={"title": "Updated"},
                headers=auth_headers,
            )
        assert any(
            "Insight updated" in r.message and insight_id in r.message
            for r in caplog.records
        )

    @pytest.mark.anyio
    async def test_delete_insight_logs_info(
        self, client, auth_headers, caplog
    ):
        """Deleting an insight logs INFO with insight_id."""
        create_response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": TEST_INSIGHT_TITLE,
                "description": TEST_DESCRIPTION,
            },
            headers=auth_headers,
        )
        insight_id = create_response.json()["id"]

        with caplog.at_level(logging.INFO, logger=MAIN_LOGGER):
            await client.delete(
                f"{INSIGHTS_ENDPOINT}/{insight_id}",
                headers=auth_headers,
            )
        assert any(
            "Insight deleted" in r.message and insight_id in r.message
            for r in caplog.records
        )

    @pytest.mark.anyio
    async def test_authorization_failure_logs_warning(
        self, client, auth_headers, engine, caplog
    ):
        """Authorization failure on update logs WARNING."""
        from sqlalchemy.orm import sessionmaker

        from app.db_models import UserDB
        from app.security import create_access_token, get_password_hash

        # Create insight as test user
        create_response = await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": TEST_INSIGHT_TITLE,
                "description": TEST_DESCRIPTION,
            },
            headers=auth_headers,
        )
        insight_id = create_response.json()["id"]

        # Create another user
        other_email = "other@example.com"
        session_factory = sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )
        with session_factory() as session:
            other_user = UserDB(
                id=uuid.uuid4(),
                email=other_email,
                name="Other User",
                hashed_password=get_password_hash("password"),
                role="advocate",
            )
            session.add(other_user)
            session.commit()

        other_token = create_access_token(data={"sub": other_email})
        other_headers = {"Authorization": f"Bearer {other_token}"}

        with caplog.at_level(logging.WARNING, logger=MAIN_LOGGER):
            await client.put(
                f"{INSIGHTS_ENDPOINT}/{insight_id}",
                json={"title": "Hacked"},
                headers=other_headers,
            )
        assert any(
            "Authorization denied" in r.message
            and r.levelno == logging.WARNING
            for r in caplog.records
        )


class TestInsightsAnalytics:
    """Tests for GET /api/v1/insights/analytics."""

    @pytest.mark.anyio
    async def test_analytics_empty(self, client, auth_headers):
        """Returns zero counts when no insights exist."""
        response = await client.get(ANALYTICS_ENDPOINT, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0
        assert data["count_by_source"] == {}
        assert data["count_by_author"] == {}
        assert len(data["insights_per_week"]) == 8

    @pytest.mark.anyio
    async def test_analytics_with_insights(self, client, auth_headers):
        """Returns correct statistics when insights exist."""
        # Create insights with different sources
        await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": "Insight 1",
                "description": "Description 1",
                "source": "community_forum",
            },
            headers=auth_headers,
        )
        await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": "Insight 2",
                "description": "Description 2",
                "source": "conference",
            },
            headers=auth_headers,
        )
        await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": "Insight 3",
                "description": "Description 3",
                "source": "community_forum",
            },
            headers=auth_headers,
        )

        response = await client.get(ANALYTICS_ENDPOINT, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 3
        assert data["count_by_source"]["community_forum"] == 2
        assert data["count_by_source"]["conference"] == 1
        assert len(data["count_by_author"]) == 1

    @pytest.mark.anyio
    async def test_analytics_insights_per_week(self, client, auth_headers):
        """Returns insights per week for last 8 weeks."""
        response = await client.get(ANALYTICS_ENDPOINT, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["insights_per_week"]) == 8
        # Verify structure of each week entry
        for week in data["insights_per_week"]:
            assert "week_start" in week
            assert "count" in week

    @pytest.mark.anyio
    async def test_analytics_without_auth_returns_401(self, client):
        """Returns 401 when no token provided."""
        response = await client.get(ANALYTICS_ENDPOINT)

        assert response.status_code == 401


class TestInsightsExport:
    """Tests for POST /api/v1/insights/export."""

    @pytest.mark.anyio
    async def test_export_creates_csv(self, client, auth_headers):
        """Creates CSV file with insights data."""
        # Create some test insights
        await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": "Test Insight",
                "description": "Test Description",
                "source": "community_forum",
            },
            headers=auth_headers,
        )

        # Mock the webhook call
        mock_response = AsyncMock()
        mock_response.status_code = 200
        with patch("httpx.AsyncClient.__aenter__") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_client.return_value = mock_instance

            response = await client.post(EXPORT_ENDPOINT, headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "exported_count" in data
            assert data["exported_count"] == 1

    @pytest.mark.anyio
    async def test_export_sends_webhook_notification(
        self, client, auth_headers
    ):
        """Sends notification to webhook after export."""
        await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": "Test",
                "description": "Test",
            },
            headers=auth_headers,
        )

        mock_response = AsyncMock()
        mock_response.status_code = 200
        with patch("httpx.AsyncClient.__aenter__") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_client.return_value = mock_instance

            response = await client.post(EXPORT_ENDPOINT, headers=auth_headers)

            assert response.status_code == 200
            # Verify webhook was called
            mock_instance.post.assert_called_once()
            call_args = mock_instance.post.call_args
            assert WEBHOOK_URL in str(call_args)

    @pytest.mark.anyio
    async def test_export_empty_insights(self, client, auth_headers):
        """Handles export when no insights exist."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        with patch("httpx.AsyncClient.__aenter__") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_client.return_value = mock_instance

            response = await client.post(EXPORT_ENDPOINT, headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["exported_count"] == 0

    @pytest.mark.anyio
    async def test_export_without_auth_returns_401(self, client):
        """Returns 401 when no token provided."""
        response = await client.post(EXPORT_ENDPOINT)

        assert response.status_code == 401

    @pytest.mark.anyio
    async def test_export_webhook_failure_still_succeeds(
        self, client, auth_headers
    ):
        """Export succeeds even if webhook fails."""
        await client.post(
            INSIGHTS_ENDPOINT,
            json={
                "title": "Test",
                "description": "Test",
            },
            headers=auth_headers,
        )

        with patch("httpx.AsyncClient.__aenter__") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post.side_effect = Exception("Webhook error")
            mock_client.return_value = mock_instance

            response = await client.post(EXPORT_ENDPOINT, headers=auth_headers)

            # Export should still succeed
            assert response.status_code == 200
