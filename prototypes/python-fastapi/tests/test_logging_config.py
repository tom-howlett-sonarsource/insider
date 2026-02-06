"""Tests for logging configuration."""
import json
import logging

from app.correlation import set_correlation_id
from app.logging_config import (
    CorrelationIdFilter,
    create_json_formatter,
    get_logger,
    setup_logging,
)

# Test constants
TEST_LOGGER_NAME = "app.test_module"
TEST_LOG_MESSAGE = "test log message"
TEST_CORRELATION_ID = "test-correlation-abc"


class TestGetLogger:
    """Tests for get_logger helper."""

    def test_returns_named_logger(self):
        """Returns a logger with the given name."""
        logger = get_logger(TEST_LOGGER_NAME)
        assert logger.name == TEST_LOGGER_NAME

    def test_returns_logging_logger_instance(self):
        """Returns a standard library Logger instance."""
        logger = get_logger(TEST_LOGGER_NAME)
        assert isinstance(logger, logging.Logger)


class TestSetupLogging:
    """Tests for setup_logging configuration."""

    def test_sets_app_logger_to_info(self):
        """Root app logger is set to INFO by default."""
        setup_logging()
        app_logger = logging.getLogger("app")
        assert app_logger.level == logging.INFO

    def test_debug_flag_sets_debug_level(self):
        """Debug flag sets app logger to DEBUG."""
        setup_logging(debug=True)
        app_logger = logging.getLogger("app")
        assert app_logger.level == logging.DEBUG
        # Reset
        setup_logging(debug=False)


class TestJsonFormatter:
    """Tests for JSON log formatter."""

    def test_outputs_valid_json(self):
        """Formatter produces valid JSON output."""
        formatter = create_json_formatter()
        record = logging.LogRecord(
            name=TEST_LOGGER_NAME,
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg=TEST_LOG_MESSAGE,
            args=None,
            exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_includes_required_fields(self):
        """JSON output includes timestamp, level, and message."""
        formatter = create_json_formatter()
        record = logging.LogRecord(
            name=TEST_LOGGER_NAME,
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg=TEST_LOG_MESSAGE,
            args=None,
            exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert "timestamp" in parsed
        assert "level" in parsed or "levelname" in parsed
        assert "message" in parsed


class TestCorrelationIdFilter:
    """Tests for CorrelationIdFilter."""

    def test_injects_correlation_id_into_record(self):
        """Filter adds correlation_id from context to log record."""
        set_correlation_id(TEST_CORRELATION_ID)
        log_filter = CorrelationIdFilter()
        record = logging.LogRecord(
            name=TEST_LOGGER_NAME,
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg=TEST_LOG_MESSAGE,
            args=None,
            exc_info=None,
        )
        log_filter.filter(record)
        assert record.correlation_id == TEST_CORRELATION_ID
        set_correlation_id(None)

    def test_injects_none_when_not_set(self):
        """Filter sets correlation_id to None when no context value."""
        set_correlation_id(None)
        log_filter = CorrelationIdFilter()
        record = logging.LogRecord(
            name=TEST_LOGGER_NAME,
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg=TEST_LOG_MESSAGE,
            args=None,
            exc_info=None,
        )
        log_filter.filter(record)
        assert record.correlation_id is None
