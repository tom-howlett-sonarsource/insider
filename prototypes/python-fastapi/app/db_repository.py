"""Database repository for insights."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db_models import InsightDB
from app.models import Insight


class InsightDBRepository:
    """Database repository for insights."""

    def __init__(self, session: Session):
        self._session = session

    def get_all(self, limit: int = 20, offset: int = 0) -> tuple[list[Insight], int]:
        """Get all insights with pagination."""
        total = self._session.query(InsightDB).count()

        db_insights = (
            self._session.query(InsightDB)
            .order_by(desc(InsightDB.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

        return [i.to_domain() for i in db_insights], total

    def get_by_id(self, insight_id: uuid.UUID) -> Insight | None:
        """Get an insight by ID."""
        db_insight = (
            self._session.query(InsightDB)
            .filter(InsightDB.id == str(insight_id))
            .first()
        )

        if not db_insight:
            return None

        return db_insight.to_domain()

    def create(self, insight: Insight) -> Insight:
        """Create a new insight."""
        db_insight = InsightDB.from_domain(insight)
        self._session.add(db_insight)
        self._session.commit()
        self._session.refresh(db_insight)
        return db_insight.to_domain()

    def update(self, insight_id: uuid.UUID, **kwargs) -> Insight | None:
        """Update an insight."""
        db_insight = (
            self._session.query(InsightDB)
            .filter(InsightDB.id == str(insight_id))
            .first()
        )

        if not db_insight:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(db_insight, key):
                if key == "source":
                    setattr(db_insight, key, value.value if value else None)
                else:
                    setattr(db_insight, key, value)

        db_insight.updated_at = datetime.now(timezone.utc)
        self._session.commit()
        self._session.refresh(db_insight)
        return db_insight.to_domain()

    def delete(self, insight_id: uuid.UUID) -> bool:
        """Delete an insight. Returns True if deleted, False if not found."""
        db_insight = (
            self._session.query(InsightDB)
            .filter(InsightDB.id == str(insight_id))
            .first()
        )

        if not db_insight:
            return False

        self._session.delete(db_insight)
        self._session.commit()
        return True
