"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.security import create_access_token, verify_password
from app.user_repository import UserDBRepository

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# Error message constants
INVALID_CREDENTIALS = "Invalid email or password"


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    """Authenticate user and return JWT token."""
    user_repo = UserDBRepository(db)
    user, hashed_password = user_repo.get_by_email_with_password(request.email)

    if not user or not hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(request.password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return TokenResponse(access_token=access_token)
