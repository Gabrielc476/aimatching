"""
Profile repository for handling user profile data access operations.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from .base_repository import BaseRepository
from models.profile import Profile

logger = logging.getLogger(__name__)


class ProfileRepository(BaseRepository[Profile]):
    """Repository for Profile model providing specialized data access operations."""

    def __init__(self, db_session: Session):
        """
        Initialize the Profile repository.

        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(Profile, db_session)

    def get_by_user_id(self, user_id: int) -> Optional[Profile]:
        """
        Get profile by user ID.

        Args:
            user_id: ID of the user

        Returns:
            Profile instance if found, None otherwise
        """
        try:
            return self.db.query(Profile).filter(Profile.user_id == user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving profile for user ID {user_id}: {str(e)}")
            return None

    def update_or_create(self, user_id: int, profile_data: Dict[str, Any]) -> Optional[Profile]:
        """
        Update an existing profile or create a new one if it doesn't exist.

        Args:
            user_id: ID of the user
            profile_data: Profile data to update or create

        Returns:
            Updated or created Profile instance if successful, None otherwise
        """
        try:
            profile = self.get_by_user_id(user_id)

            if profile:
                # Update existing profile
                for key, value in profile_data.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)
                self.db.commit()
                self.db.refresh(profile)
                return profile
            else:
                # Create new profile
                profile_data['user_id'] = user_id
                return self.create(profile_data)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating or creating profile for user ID {user_id}: {str(e)}")
            return None

    def get_profiles_by_skills(self, skills: List[str], skip: int = 0, limit: int = 100) -> List[Profile]:
        """
        Find profiles that have specific skills.

        Args:
            skills: List of skills to match
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Profile instances matching the skills criteria
        """
        try:
            # Construct a query to match profiles with any of the specified skills
            # Note: This implementation depends on how skills are stored in your database
            # Assuming skills is a JSON array in PostgreSQL
            profiles = []
            for skill in skills:
                # Using JSON containment operator for array items - PostgreSQL specific
                skill_matches = self.db.query(Profile).filter(
                    Profile.skills.contains([skill])
                ).offset(skip).limit(limit).all()

                # Add unique profiles to the result list
                for profile in skill_matches:
                    if profile not in profiles:
                        profiles.append(profile)

                if len(profiles) >= limit:
                    break

            return profiles
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving profiles by skills {skills}: {str(e)}")
            return []

    def get_profiles_by_location(self, location: str, skip: int = 0, limit: int = 100) -> List[Profile]:
        """
        Find profiles by location.

        Args:
            location: Location to match (partial match is supported)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Profile instances matching the location criteria
        """
        try:
            return self.db.query(Profile).filter(
                Profile.location.ilike(f"%{location}%")
            ).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving profiles by location {location}: {str(e)}")
            return []

    def get_profiles_by_experience_level(self, experience_level: str, skip: int = 0, limit: int = 100) -> List[Profile]:
        """
        Find profiles by experience level.

        Args:
            experience_level: Experience level to match
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Profile instances matching the experience level
        """
        try:
            return self.db.query(Profile).filter(
                Profile.experience_level == experience_level
            ).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving profiles by experience level {experience_level}: {str(e)}")
            return []

    def update_skills(self, profile_id: int, skills: List[str]) -> Optional[Profile]:
        """
        Update the skills of a profile.

        Args:
            profile_id: ID of the profile
            skills: List of skills to set

        Returns:
            Updated Profile instance if successful, None otherwise
        """
        try:
            profile = self.get_by_id(profile_id)
            if not profile:
                return None

            profile.skills = skills
            self.db.commit()
            self.db.refresh(profile)
            return profile
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating skills for profile ID {profile_id}: {str(e)}")
            return None

    def update_job_preferences(self, profile_id: int, job_preferences: Dict[str, Any]) -> Optional[Profile]:
        """
        Update job preferences for a profile.

        Args:
            profile_id: ID of the profile
            job_preferences: Dictionary of job preferences

        Returns:
            Updated Profile instance if successful, None otherwise
        """
        try:
            profile = self.get_by_id(profile_id)
            if not profile:
                return None

            profile.job_preferences = job_preferences
            self.db.commit()
            self.db.refresh(profile)
            return profile
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating job preferences for profile ID {profile_id}: {str(e)}")
            return None