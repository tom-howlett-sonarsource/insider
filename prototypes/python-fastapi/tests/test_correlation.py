"""Tests for correlation ID context management."""
import uuid

from app.correlation import (
    generate_correlation_id,
    get_correlation_id,
    set_correlation_id,
)


class TestCorrelationId:
    """Tests for correlation ID context variable."""

    def test_default_is_none(self):
        """Correlation ID is None when not set."""
        assert get_correlation_id() is None

    def test_set_and_get_roundtrip(self):
        """Can set and retrieve a correlation ID."""
        test_id = "test-correlation-123"
        token = set_correlation_id(test_id)
        assert get_correlation_id() == test_id
        # Reset for other tests
        set_correlation_id(None)

    def test_generate_returns_uuid_string(self):
        """Generated correlation ID is a valid UUID string."""
        cid = generate_correlation_id()
        # Should be a valid UUID
        parsed = uuid.UUID(cid)
        assert str(parsed) == cid

    def test_generate_returns_unique_values(self):
        """Each call to generate returns a unique ID."""
        ids = {generate_correlation_id() for _ in range(10)}
        assert len(ids) == 10
