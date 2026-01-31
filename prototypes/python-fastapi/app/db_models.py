"""SQLAlchemy database models."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models import Insight, Source


class InsightDB(Base):
    """SQLAlchemy model for insights table."""

    __tablename__ = "insights"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    author_id: Mapped[str] = mapped_column(String(36), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __init__(
        self,
        id: uuid.UUID,
        author_id: uuid.UUID,
        title: str,
        description: str,
        source: str | None = None,
    ):
        self.id = str(id)
        self.author_id = str(author_id)
        self.title = title
        self.description = description
        self.source = source

    def to_domain(self) -> Insight:
        """Convert to domain model."""
        return Insight(
            id=uuid.UUID(self.id),
            author_id=uuid.UUID(self.author_id),
            title=self.title,
            description=self.description,
            source=Source(self.source) if self.source else None,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, insight: Insight) -> "InsightDB":
        """Create from domain model."""
        return cls(
            id=insight.id,
            author_id=insight.author_id,
            title=insight.title,
            description=insight.description,
            source=insight.source.value if insight.source else None,
        )
