"""
Base repository implementing the repository pattern for data access.
"""

from typing import Generic, TypeVar, Type, List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..session import Base
import logging

# Generic type for SQLAlchemy models
T = TypeVar('T', bound=Base)

logger = logging.getLogger(__name__)

class BaseRepository(Generic[T]):
    """
    Base repository implementing common CRUD operations.

    This class follows the Repository pattern to abstract the data access layer.
    """

    def __init__(self, model_class: Type[T], db_session: Session):
        """
        Initialize the repository with a model class and database session.

        Args:
            model_class: The SQLAlchemy model class
            db_session: SQLAlchemy database session
        """
        self.model_class = model_class
        self.db = db_session

    def get_by_id(self, entity_id: int) -> Optional[T]:
        """
        Retrieve an entity by its ID.

        Args:
            entity_id: The primary key of the entity

        Returns:
            The entity if found, None otherwise
        """
        try:
            return self.db.query(self.model_class).filter(self.model_class.id == entity_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving {self.model_class.__name__} with ID {entity_id}: {str(e)}")
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Retrieve all entities with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of entities
        """
        try:
            return self.db.query(self.model_class).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving all {self.model_class.__name__}: {str(e)}")
            return []

    def create(self, data: Dict[str, Any]) -> Optional[T]:
        """
        Create a new entity.

        Args:
            data: Dictionary of entity attributes

        Returns:
            The created entity if successful, None otherwise
        """
        try:
            entity = self.model_class(**data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating {self.model_class.__name__}: {str(e)}")
            return None

    def update(self, entity_id: int, data: Dict[str, Any]) -> Optional[T]:
        """
        Update an existing entity.

        Args:
            entity_id: The primary key of the entity
            data: Dictionary of entity attributes to update

        Returns:
            The updated entity if successful, None otherwise
        """
        try:
            entity = self.get_by_id(entity_id)
            if not entity:
                return None

            for key, value in data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            self.db.commit()
            self.db.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating {self.model_class.__name__} with ID {entity_id}: {str(e)}")
            return None

    def delete(self, entity_id: int) -> bool:
        """
        Delete an entity by its ID.

        Args:
            entity_id: The primary key of the entity

        Returns:
            True if successfully deleted, False otherwise
        """
        try:
            entity = self.get_by_id(entity_id)
            if not entity:
                return False

            self.db.delete(entity)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model_class.__name__} with ID {entity_id}: {str(e)}")
            return False

    def exists(self, entity_id: int) -> bool:
        """
        Check if an entity exists by its ID.

        Args:
            entity_id: The primary key of the entity

        Returns:
            True if entity exists, False otherwise
        """
        try:
            return self.db.query(self.model_class.id).filter(
                self.model_class.id == entity_id
            ).scalar() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model_class.__name__} with ID {entity_id}: {str(e)}")
            return False

    def count(self) -> int:
        """
        Count all entities.

        Returns:
            Total number of entities
        """
        try:
            return self.db.query(self.model_class).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model_class.__name__}: {str(e)}")
            return 0

    def filter_by(self, skip: int = 0, limit: int = 100, **kwargs) -> List[T]:
        """
        Filter entities by attributes.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            **kwargs: Filter criteria as keyword arguments

        Returns:
            List of filtered entities
        """
        try:
            return self.db.query(self.model_class).filter_by(**kwargs).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error filtering {self.model_class.__name__}: {str(e)}")
            return []
