"""User endpoints."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/api/v1/users", tags=["users"])


class UserResponse(BaseModel):
    """User response schema."""

    id: str
    email: str
    name: str
    role: str


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated user information."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value,
    )
