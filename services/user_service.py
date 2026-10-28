"""User service — business logic for user management."""

from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateUserError, UserNotFoundError
from app.core.logging import get_logger
from app.database.models.user import User
from app.schemas.user import UserCreate, UserUpdate

logger = get_logger(__name__)

import bcrypt


def _hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


class UserService:
    """Service class for user-related operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_user(self, payload: UserCreate) -> User:
        """Create a new user with a hashed password.

        Args:
            payload: Validated user creation data.

        Returns:
            The newly created User ORM instance.

        Raises:
            DuplicateUserError: If the e-mail is already registered.
        """
        existing = self.db.query(User).filter(User.email == payload.email).first()
        if existing:
            logger.warning("Duplicate user creation attempt for email: %s", payload.email)
            raise DuplicateUserError()

        user = User(
            name=payload.name,
            email=payload.email,
            password_hash=_hash_password(payload.password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        logger.info("Created user id=%d email=%s", user.id, user.email)
        return user

    def get_user(self, user_id: int) -> User:
        """Retrieve a user by ID.

        Args:
            user_id: The primary key of the user.

        Returns:
            The User ORM instance.

        Raises:
            UserNotFoundError: If no user exists with the given ID.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError()
        return user

    def update_user(self, user_id: int, payload: UserUpdate) -> User:
        """Update editable profile fields for a user."""
        user = self.get_user(user_id)
        user.name = payload.name.strip()
        self.db.commit()
        self.db.refresh(user)
        return user
