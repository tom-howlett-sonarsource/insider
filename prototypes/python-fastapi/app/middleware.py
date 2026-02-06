"""Request logging middleware with correlation ID support."""
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.correlation import generate_correlation_id, set_correlation_id
from app.logging_config import get_logger

logger = get_logger("app.middleware")

CORRELATION_ID_HEADER = "X-Correlation-ID"


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs requests and manages correlation IDs."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with logging and correlation ID."""
        correlation_id = request.headers.get(
            CORRELATION_ID_HEADER, generate_correlation_id()
        )
        set_correlation_id(correlation_id)

        logger.info(
            "Request received: %s %s", request.method, request.url.path
        )

        start_time = time.monotonic()
        response = await call_next(request)
        duration_ms = round((time.monotonic() - start_time) * 1000, 2)

        logger.info(
            "Request completed: %s %s status=%d duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        response.headers[CORRELATION_ID_HEADER] = correlation_id
        return response
