"""Correlation ID context management using contextvars."""
import uuid
from contextvars import ContextVar

correlation_id_var: ContextVar[str | None] = ContextVar(
    "correlation_id", default=None
)


def get_correlation_id() -> str | None:
    """Get the current correlation ID from context."""
    return correlation_id_var.get()


def set_correlation_id(value: str | None) -> object:
    """Set the correlation ID in context. Returns the token for reset."""
    return correlation_id_var.set(value)


def generate_correlation_id() -> str:
    """Generate a new unique correlation ID."""
    return str(uuid.uuid4())
