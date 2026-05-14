"""Database repository for insights."""
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.db_models import InsightDB
from app.logging_config import get_logger
from app.models import Insight

logger = get_logger("app.repository.insight")


class InsightDBRepository:
    """Database repository for insights."""

    def __init__(self, session: Session):
        self._session = session

    def get_all(self, limit: int = 20, offset: int = 0) -> tuple[list[Insight], int]:
        """Get all insights with pagination."""
        logger.debug("get_all: limit=%d offset=%d", limit, offset)
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
        logger.debug("get_by_id: insight_id=%s", insight_id)
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
        logger.debug("create: insight_id=%s", insight.id)
        db_insight = InsightDB.from_domain(insight)
        self._session.add(db_insight)
        self._session.commit()
        self._session.refresh(db_insight)
        return db_insight.to_domain()

    def update(self, insight_id: uuid.UUID, **kwargs) -> Insight | None:
        """Update an insight."""
        logger.debug("update: insight_id=%s", insight_id)
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
        logger.debug("delete: insight_id=%s", insight_id)
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

    def get_analytics(self) -> dict:
        """Get analytics data about insights."""
        logger.debug("get_analytics")

        # Total count
        total_count = self._session.query(InsightDB).count()

        # Count by source
        source_counts = (
            self._session.query(InsightDB.source, func.count(InsightDB.id))
            .filter(InsightDB.source.isnot(None))
            .group_by(InsightDB.source)
            .all()
        )
        count_by_source = dict(source_counts)

        # Count by author
        author_counts = (
            self._session.query(
                InsightDB.author_id, func.count(InsightDB.id)
            )
            .group_by(InsightDB.author_id)
            .all()
        )
        count_by_author = dict(author_counts)

        # Insights per week for last 8 weeks
        now = datetime.now(timezone.utc)
        insights_per_week = []

        for week_offset in range(8):
            week_start = now - timedelta(weeks=week_offset + 1)
            week_end = now - timedelta(weeks=week_offset)

            count = (
                self._session.query(InsightDB)
                .filter(
                    InsightDB.created_at >= week_start,
                    InsightDB.created_at < week_end,
                )
                .count()
            )

            insights_per_week.append(
                {"week_start": week_start, "count": count}
            )

        # Reverse to show oldest week first
        insights_per_week.reverse()

        return {
            "total_count": total_count,
            "count_by_source": count_by_source,
            "count_by_author": count_by_author,
            "insights_per_week": insights_per_week,
        }

    def get_all_for_export(self) -> list[Insight]:
        """Get all insights for export (no pagination)."""
        logger.debug("get_all_for_export")
        db_insights = (
            self._session.query(InsightDB)
            .order_by(desc(InsightDB.created_at))
            .all()
        )
        return [i.to_domain() for i in db_insights]
