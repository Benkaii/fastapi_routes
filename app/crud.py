from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate
from app.security import hash_password


def get_user_by_username(
    db: Session,
    username: str,
) -> User | None:
    """Retrieve a user by username."""
    statement = select(User).where(User.username == username)
    return db.scalar(statement)


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    """Retrieve a user by email address."""
    statement = select(User).where(User.email == email)
    return db.scalar(statement)


def create_user(
    db: Session,
    user_data: UserCreate,
) -> User:
    """Create a user and store only the hashed password."""
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user