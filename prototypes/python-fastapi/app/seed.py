"""Seed data for development."""
import uuid

from sqlalchemy.orm import Session

from app.db_models import UserDB
from app.logging_config import get_logger
from app.security import get_password_hash

logger = get_logger("app.seed")

# Default seed users for development
SEED_USERS = [
    {
        "email": "advocate@example.com",
        "name": "Test Advocate",
        "password": "password123",
        "role": "advocate",
    },
    {
        "email": "pm@example.com",
        "name": "Test PM",
        "password": "password123",
        "role": "product_manager",
    },
]


def seed_users(session: Session) -> None:
    """Seed default users if they don't exist."""
    for user_data in SEED_USERS:
        existing = (
            session.query(UserDB)
            .filter(UserDB.email == user_data["email"])
            .first()
        )
        if not existing:
            user = UserDB(
                id=uuid.uuid4(),
                email=user_data["email"],
                name=user_data["name"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
            )
            session.add(user)
            logger.info("Seeded user: %s", user_data["email"])
    session.commit()
