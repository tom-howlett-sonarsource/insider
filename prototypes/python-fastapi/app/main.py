"""FastAPI application entry point."""
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status

from app.models import Insight
from app.repository import insight_repository
from app.schemas import (
    InsightCreate,
    InsightListResponse,
    InsightResponse,
    InsightUpdate,
)

# Error message constants
INSIGHT_NOT_FOUND = "Insight not found"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    # Clear repository on startup (for testing isolation)
    insight_repository.clear()
    yield
    # Cleanup on shutdown
    insight_repository.clear()


app = FastAPI(
    title="Insider",
    description="Product insights tracker for Developer Advocates",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/api/v1/insights", response_model=InsightListResponse)
async def list_insights(limit: int = 20, offset: int = 0):
    """List all insights."""
    insights, total = insight_repository.get_all(limit=limit, offset=offset)
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
async def create_insight(insight_data: InsightCreate):
    """Create a new insight."""
    # For now, use a placeholder author_id (auth will come later)
    insight = Insight(
        title=insight_data.title,
        description=insight_data.description,
        source=insight_data.source,
        author_id=uuid.uuid4(),  # Placeholder
    )
    created = insight_repository.create(insight)
    return InsightResponse(**created.model_dump())


@app.get("/api/v1/insights/{insight_id}", response_model=InsightResponse)
async def get_insight(insight_id: uuid.UUID):
    """Get an insight by ID."""
    insight = insight_repository.get_by_id(insight_id)
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=INSIGHT_NOT_FOUND,
        )
    return InsightResponse(**insight.model_dump())


@app.put("/api/v1/insights/{insight_id}", response_model=InsightResponse)
async def update_insight(insight_id: uuid.UUID, insight_data: InsightUpdate):
    """Update an insight."""
    update_data = insight_data.model_dump(exclude_unset=True)
    updated = insight_repository.update(insight_id, **update_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=INSIGHT_NOT_FOUND,
        )
    return InsightResponse(**updated.model_dump())


@app.delete(
    "/api/v1/insights/{insight_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_insight(insight_id: uuid.UUID):
    """Delete an insight."""
    deleted = insight_repository.delete(insight_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=INSIGHT_NOT_FOUND,
        )
    return None
