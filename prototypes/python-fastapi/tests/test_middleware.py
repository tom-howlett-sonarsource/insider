"""Tests for request logging middleware."""
import logging
import uuid

import pytest

# Test constants
CORRELATION_ID_HEADER = "X-Correlation-ID"
INSIGHTS_ENDPOINT = "/api/v1/insights"
REQUEST_RECEIVED_MSG = "Request received"
REQUEST_COMPLETED_MSG = "Request completed"


class TestLoggingMiddleware:
    """Tests for request logging middleware."""

    @pytest.mark.anyio
    async def test_response_includes_correlation_id_header(
        self, client, auth_headers
    ):
        """Response includes X-Correlation-ID header with a UUID."""
        response = await client.get(INSIGHTS_ENDPOINT, headers=auth_headers)
        correlation_id = response.headers.get(CORRELATION_ID_HEADER)
        assert correlation_id is not None
        # Should be a valid UUID
        uuid.UUID(correlation_id)

    @pytest.mark.anyio
    async def test_incoming_correlation_id_is_preserved(
        self, client, auth_headers
    ):
        """Incoming X-Correlation-ID is preserved in response."""
        incoming_id = "test-incoming-correlation-id"
        headers = {**auth_headers, CORRELATION_ID_HEADER: incoming_id}
        response = await client.get(INSIGHTS_ENDPOINT, headers=headers)
        assert response.headers.get(CORRELATION_ID_HEADER) == incoming_id

    @pytest.mark.anyio
    async def test_logs_request_received(
        self, client, auth_headers, caplog
    ):
        """Logs 'Request received' at INFO level."""
        with caplog.at_level(logging.INFO, logger="app.middleware"):
            await client.get(INSIGHTS_ENDPOINT, headers=auth_headers)
        assert any(
            REQUEST_RECEIVED_MSG in record.message
            for record in caplog.records
        )

    @pytest.mark.anyio
    async def test_logs_request_completed_with_status_and_duration(
        self, client, auth_headers, caplog
    ):
        """Logs 'Request completed' at INFO with status code and duration."""
        with caplog.at_level(logging.INFO, logger="app.middleware"):
            await client.get(INSIGHTS_ENDPOINT, headers=auth_headers)
        completed_records = [
            r for r in caplog.records if REQUEST_COMPLETED_MSG in r.message
        ]
        assert len(completed_records) >= 1
        record = completed_records[0]
        assert "status" in record.message.lower() or hasattr(
            record, "status_code"
        )
        assert "duration" in record.message.lower() or hasattr(
            record, "duration_ms"
        )
