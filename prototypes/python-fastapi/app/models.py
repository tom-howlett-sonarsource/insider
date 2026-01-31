"""Domain models for Insider."""
import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Source(str, Enum):
    """Source of an insight."""

    COMMUNITY_FORUM = "community_forum"
    CONFERENCE = "conference"
    SOCIAL_MEDIA = "social_media"
    MEETUP = "meetup"
    OTHER = "other"


class Role(str, Enum):
    """User role."""

    ADVOCATE = "advocate"
    PRODUCT_MANAGER = "product_manager"


class Insight(BaseModel):
    """A product insight captured by a Developer Advocate."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    author_id: uuid.UUID
    title: str = Field(..., max_length=200)
    description: str
    source: Source | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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


class Product(BaseModel):
    """A product or feature that insights can be linked to."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    description: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v


class Tag(BaseModel):
    """A tag for organizing insights."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("name")
    @classmethod
    def name_not_empty_and_lowercase(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.lower()


class User(BaseModel):
    """A user of the system."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    email: str
    name: str
    role: Role
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("email")
    @classmethod
    def email_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Email cannot be empty")
        return v
