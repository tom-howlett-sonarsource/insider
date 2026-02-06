"""Logging configuration with JSON formatting and correlation ID support."""
import logging
import sys

from pythonjsonlogger.json import JsonFormatter

from app.correlation import get_correlation_id


class CorrelationIdFilter(logging.Filter):
    """Logging filter that injects correlation_id from contextvars."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation_id to every log record."""
        record.correlation_id = get_correlation_id()
        return True


def create_json_formatter() -> JsonFormatter:
    """Create a JSON formatter with standard fields."""
    return JsonFormatter(
        fmt="%(timestamp)s %(level)s %(name)s %(message)s %(correlation_id)s",
        rename_fields={
            "levelname": "level",
            "asctime": "timestamp",
        },
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def setup_logging(debug: bool = False) -> None:
    """Configure structured JSON logging for the application.

    Sets up the 'app' logger hierarchy with JSON output to stdout.
    Suppresses noisy third-party loggers.
    """
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Only add handler if none exist (avoid duplicates on reload)
    if not app_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(create_json_formatter())
        handler.addFilter(CorrelationIdFilter())
        app_logger.addHandler(handler)

    # Suppress noisy third-party loggers
    for noisy_logger in ("uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger."""
    return logging.getLogger(name)
