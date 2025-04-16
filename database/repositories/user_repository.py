"""
User repository for handling user data access operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from .base_repository import BaseRepository
from models.user import User

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """Repository for User model providing specialized data access operations."""

    def __init__(self, db_session: Session):
        """
        Initialize the User repository.

        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(User, db_session)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Find a user by email address.

        Args:
            email: User's email address

        Returns:
            User instance if found, None otherwise
        """
        try:
            return self.db.query(User).filter(User.email == email).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving user by email {email}: {str(e)}")
            return None

    def email_exists(self, email: str) -> bool:
        """
        Check if a user with the given email exists.

        Args:
            email: Email address to check

        Returns:
            True if exists, False otherwise
        """
        try:
            return self.db.query(User.id).filter(User.email == email).scalar() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking if email {email} exists: {str(e)}")
            return False

    def get_users_by_ids(self, user_ids: List[int]) -> List[User]:
        """
        Retrieve multiple users by their IDs.

        Args:
            user_ids: List of user IDs

        Returns:
            List of User instances
        """
        try:
            return self.db.query(User).filter(User.id.in_(user_ids)).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving users by IDs {user_ids}: {str(e)}")
            return []

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Retrieve all active users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active User instances
        """
        try:
            return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving active users: {str(e)}")
            return []

    def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate a user without deleting the record.

        Args:
            user_id: User ID to deactivate

        Returns:
            True if successful, False otherwise
        """
        try:
            user = self.get_by_id(user_id)
            if not user:
                return False

            user.is_active = False
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deactivating user with ID {user_id}: {str(e)}")
            return False

    def get_users_with_resumes(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Retrieve users who have uploaded at least one resume.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of User instances with resumes
        """
        try:
            return self.db.query(User).filter(User.resumes.any()).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving users with resumes: {str(e)}")
            return []

    def count_users_registered_since(self, since_date) -> int:
        """
        Count users registered since a specific date.

        Args:
            since_date: Date threshold

        Returns:
            Count of users registered since the specified date
        """
        try:
            return self.db.query(User).filter(User.created_at >= since_date).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting users registered since {since_date}: {str(e)}")
            return 0