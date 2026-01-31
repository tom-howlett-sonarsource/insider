"""FastAPI application entry point."""
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal, create_tables, get_db
from app.db_repository import InsightDBRepository
from app.dependencies import get_current_user
from app.models import Insight, User
from app.routers import auth, users
from app.seed import seed_users
from app.schemas import (
    InsightCreate,
    InsightListResponse,
    InsightResponse,
    InsightUpdate,
)

# Error message constants
INSIGHT_NOT_FOUND = "Insight not found"
NOT_AUTHORIZED = "Not authorized to modify this insight"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    create_tables()
    # Seed default users for development
    with SessionLocal() as session:
        seed_users(session)
    yield


app = FastAPI(
    title="Insider",
    description="Product insights tracker for Developer Advocates",
    version="0.1.0",
    lifespan=lifespan,
)

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
    return InsightResponse(**created.model_dump())


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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=NOT_AUTHORIZED,
        )

    update_data = insight_data.model_dump(exclude_unset=True)
    updated = repository.update(insight_id, **update_data)
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=NOT_AUTHORIZED,
        )

    repository.delete(insight_id)
    return None
