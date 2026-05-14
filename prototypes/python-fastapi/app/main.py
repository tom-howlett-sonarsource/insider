"""FastAPI application entry point."""
import csv
import tempfile
import uuid
from contextlib import asynccontextmanager

import aiofiles
import httpx
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal, create_tables, get_db
from app.db_repository import InsightDBRepository
from app.dependencies import get_current_user
from app.logging_config import get_logger, setup_logging
from app.middleware import LoggingMiddleware
from app.models import Insight, User
from app.routers import auth, users
from app.seed import seed_users
from app.schemas import (
    AnalyticsResponse,
    ExportResponse,
    InsightCreate,
    InsightListResponse,
    InsightResponse,
    InsightUpdate,
    WeeklyInsightCount,
)

logger = get_logger("app.main")

# Error message constants
INSIGHT_NOT_FOUND = "Insight not found"
NOT_AUTHORIZED = "Not authorized to modify this insight"
EXPORT_SUCCESS = "Insights exported successfully"
ANALYTICS_WEBHOOK_URL = "https://hooks.example.com/notify"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    setup_logging()
    logger.info("Insider API starting up")
    create_tables()
    # Seed default users for development
    with SessionLocal() as session:
        seed_users(session)
    yield
    logger.info("Insider API shutting down")


app = FastAPI(
    title="Insider",
    description="Product insights tracker for Developer Advocates",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)


def get_repository(db: Session = Depends(get_db)) -> InsightDBRepository:
    """Dependency that provides an insight repository."""
    return InsightDBRepository(db)


@app.get("/api/v1/insights", response_model=InsightListResponse)
async def list_insights(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    repository: InsightDBRepository = Depends(get_repository),
):
    """List all insights."""
    insights, total = repository.get_all(limit=limit, offset=offset)
    return InsightListResponse(
        items=[InsightResponse(**i.model_dump()) for i in insights],
        total=total,
        limit=limit,
        offset=offset,
    )


@app.post(
    "/api/v1/insights",
    response_model=InsightResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_insight(
    insight_data: InsightCreate,
    current_user: User = Depends(get_current_user),
    repository: InsightDBRepository = Depends(get_repository),
):
    """Create a new insight."""
    insight = Insight(
        title=insight_data.title,
        description=insight_data.description,
        source=insight_data.source,
        author_id=current_user.id,
    )
    created = repository.create(insight)
    logger.info(
        "Insight created: insight_id=%s user_id=%s",
        created.id,
        current_user.id,
    )
    return InsightResponse(**created.model_dump())


@app.get("/api/v1/insights/analytics", response_model=AnalyticsResponse)
def get_analytics(
    current_user: User = Depends(get_current_user),
    repository: InsightDBRepository = Depends(get_repository),
):
    """Get analytics about insights."""
    analytics = repository.get_analytics()

    return AnalyticsResponse(
        total_count=analytics["total_count"],
        count_by_source=analytics["count_by_source"],
        count_by_author=analytics["count_by_author"],
        insights_per_week=[
            WeeklyInsightCount(
                week_start=week["week_start"], count=week["count"]
            )
            for week in analytics["insights_per_week"]
        ],
    )


@app.post("/api/v1/insights/export", response_model=ExportResponse)
async def export_insights(
    current_user: User = Depends(get_current_user),
    repository: InsightDBRepository = Depends(get_repository),
):
    """Export all insights to CSV and send notification."""
    insights = repository.get_all_for_export()

    # Create CSV in temporary file using async file operations
    temp_file = tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".csv"
    )
    temp_file_path = temp_file.name
    temp_file.close()

    async with aiofiles.open(temp_file_path, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        await csvfile.write(
            ",".join(
                ["id", "title", "description", "source", "author_id", "created_at"]
            )
            + "\n"
        )

        for insight in insights:
            row = [
                str(insight.id),
                insight.title,
                insight.description,
                insight.source.value if insight.source else "",
                str(insight.author_id),
                insight.created_at.isoformat(),
            ]
            await csvfile.write(",".join(f'"{field}"' for field in row) + "\n")

    # Send webhook notification
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                ANALYTICS_WEBHOOK_URL,
                json={
                    "event": "insights_exported",
                    "count": len(insights),
                    "user_id": str(current_user.id),
                },
                timeout=5.0,
            )
        logger.info(
            "Export notification sent: count=%d user_id=%s",
            len(insights),
            current_user.id,
        )
    except Exception as e:
        logger.warning("Failed to send export notification: %s", str(e))

    logger.info(
        "Insights exported: count=%d user_id=%s",
        len(insights),
        current_user.id,
    )

    return ExportResponse(
        message=EXPORT_SUCCESS,
        exported_count=len(insights),
    )


@app.get("/api/v1/insights/{insight_id}", response_model=InsightResponse)
async def get_insight(
    insight_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    repository: InsightDBRepository = Depends(get_repository),
):
    """Get an insight by ID."""
    insight = repository.get_by_id(insight_id)
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=INSIGHT_NOT_FOUND,
        )
    return InsightResponse(**insight.model_dump())


@app.put("/api/v1/insights/{insight_id}", response_model=InsightResponse)
async def update_insight(
    insight_id: uuid.UUID,
    insight_data: InsightUpdate,
    current_user: User = Depends(get_current_user),
    repository: InsightDBRepository = Depends(get_repository),
):
    """Update an insight."""
    insight = repository.get_by_id(insight_id)
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=INSIGHT_NOT_FOUND,
        )

    # Check if user is the author
    if insight.author_id != current_user.id:
        logger.warning(
            "Authorization denied: user_id=%s attempted to update insight_id=%s owned by %s",
            current_user.id,
            insight_id,
            insight.author_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=NOT_AUTHORIZED,
        )

    update_data = insight_data.model_dump(exclude_unset=True)
    updated = repository.update(insight_id, **update_data)
    logger.info(
        "Insight updated: insight_id=%s user_id=%s",
        insight_id,
        current_user.id,
    )
    return InsightResponse(**updated.model_dump())


@app.delete(
    "/api/v1/insights/{insight_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_insight(
    insight_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    repository: InsightDBRepository = Depends(get_repository),
):
    """Delete an insight."""
    insight = repository.get_by_id(insight_id)
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=INSIGHT_NOT_FOUND,
        )

    # Check if user is the author
    if insight.author_id != current_user.id:
        logger.warning(
            "Authorization denied: user_id=%s attempted to delete insight_id=%s owned by %s",
            current_user.id,
            insight_id,
            insight.author_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=NOT_AUTHORIZED,
        )

    repository.delete(insight_id)
    logger.info(
        "Insight deleted: insight_id=%s user_id=%s",
        insight_id,
        current_user.id,
    )
    return None
