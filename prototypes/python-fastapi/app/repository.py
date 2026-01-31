"""In-memory repository for storing data (will be replaced with DB later)."""
import uuid
from datetime import datetime, timezone

from app.models import Insight


class InsightRepository:
    """In-memory storage for insights."""

    def __init__(self):
        self._insights: dict[uuid.UUID, Insight] = {}

    def get_all(self, limit: int = 20, offset: int = 0) -> tuple[list[Insight], int]:
        """Get all insights with pagination."""
        all_insights = list(self._insights.values())
        # Sort by created_at descending (most recent first)
        all_insights.sort(key=lambda x: x.created_at, reverse=True)
        total = len(all_insights)
        return all_insights[offset : offset + limit], total

    def get_by_id(self, insight_id: uuid.UUID) -> Insight | None:
        """Get an insight by ID."""
        return self._insights.get(insight_id)

    def create(self, insight: Insight) -> Insight:
        """Create a new insight."""
        self._insights[insight.id] = insight
        return insight

    def update(self, insight_id: uuid.UUID, **kwargs) -> Insight | None:
        """Update an insight."""
        insight = self._insights.get(insight_id)
        if not insight:
            return None

        # Update fields
        insight_dict = insight.model_dump()
        for key, value in kwargs.items():
            if value is not None:
                insight_dict[key] = value
        insight_dict["updated_at"] = datetime.now(timezone.utc)

        updated_insight = Insight(**insight_dict)
        self._insights[insight_id] = updated_insight
        return updated_insight

    def delete(self, insight_id: uuid.UUID) -> bool:
        """Delete an insight. Returns True if deleted, False if not found."""
        if insight_id in self._insights:
            del self._insights[insight_id]
            return True
        return False

    def clear(self):
        """Clear all insights (for testing)."""
        self._insights.clear()


# Global repository instance (will be replaced with DI later)
insight_repository = InsightRepository()
