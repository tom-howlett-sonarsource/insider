"""API request/response schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models import Source


class InsightCreate(BaseModel):
    """Schema for creating an insight."""

    title: str = Field(..., max_length=200)
    description: str
    source: Source | None = None
    product_ids: list[uuid.UUID] | None = None
    tags: list[str] | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v

    @field_validator("description")
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Description cannot be empty")
        return v


class InsightUpdate(BaseModel):
    """Schema for updating an insight."""

    title: str | None = Field(None, max_length=200)
    description: str | None = None
    source: Source | None = None
    product_ids: list[uuid.UUID] | None = None
    tags: list[str] | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty")
        return v


class InsightResponse(BaseModel):
    """Schema for insight response."""

    id: uuid.UUID
    title: str
    description: str
    source: Source | None = None
    created_at: datetime
    updated_at: datetime


class InsightListResponse(BaseModel):
    """Schema for list of insights response."""

    items: list[InsightResponse]
    total: int
    limit: int = 20
    offset: int = 0
