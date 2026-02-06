"""Shared FastAPI dependencies."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging_config import get_logger
from app.models import User
from app.security import decode_token
from app.user_repository import UserDBRepository

logger = get_logger("app.security")

security = HTTPBearer()

# Error message constant
CREDENTIALS_EXCEPTION_DETAIL = "Could not validate credentials"


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Dependency that returns the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=CREDENTIALS_EXCEPTION_DETAIL,
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(credentials.credentials)
        email: str | None = payload.get("sub")
        if email is None:
            logger.warning("JWT token missing subject claim")
            raise credentials_exception
    except JWTError:
        logger.warning("Invalid or expired JWT token")
        raise credentials_exception

    user_repo = UserDBRepository(db)
    user = user_repo.get_by_email(email)
    if user is None:
        logger.warning("User not found for email in JWT: %s", email)
        raise credentials_exception

    return user
