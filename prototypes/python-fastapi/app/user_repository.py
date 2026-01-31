"""Database repository for users."""
import uuid

from sqlalchemy.orm import Session

from app.db_models import UserDB
from app.models import User


class UserDBRepository:
    """Database repository for users."""

    def __init__(self, session: Session):
        self._session = session

    def get_by_email(self, email: str) -> User | None:
        """Get a user by email."""
        db_user = (
            self._session.query(UserDB).filter(UserDB.email == email).first()
        )

        if not db_user:
            return None

        return db_user.to_domain()

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Get a user by ID."""
        db_user = (
            self._session.query(UserDB)
            .filter(UserDB.id == str(user_id))
            .first()
        )

        if not db_user:
            return None

        return db_user.to_domain()

    def get_by_email_with_password(
        self, email: str
    ) -> tuple[User | None, str | None]:
        """Get a user by email along with their hashed password.

        Returns a tuple of (User, hashed_password) for auth verification.
        """
        db_user = (
            self._session.query(UserDB).filter(UserDB.email == email).first()
        )

        if not db_user:
            return None, None

        return db_user.to_domain(), db_user.hashed_password
