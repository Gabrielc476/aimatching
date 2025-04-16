"""
Resume repository for handling resume data access operations.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from .base_repository import BaseRepository
from models.resume import Resume

logger = logging.getLogger(__name__)


class ResumeRepository(BaseRepository[Resume]):
    """Repository for Resume model providing specialized data access operations."""

    def __init__(self, db_session: Session):
        """
        Initialize the Resume repository.

        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(Resume, db_session)

    def get_user_resumes(self, user_id: int) -> List[Resume]:
        """
        Get all resumes for a specific user.

        Args:
            user_id: ID of the user

        Returns:
            List of Resume instances for the user
        """
        try:
            return self.db.query(Resume).filter(Resume.user_id == user_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving resumes for user ID {user_id}: {str(e)}")
            return []

    def get_primary_resume(self, user_id: int) -> Optional[Resume]:
        """
        Get the primary resume for a user.

        Args:
            user_id: ID of the user

        Returns:
            Primary Resume instance if found, None otherwise
        """
        try:
            return self.db.query(Resume).filter(
                Resume.user_id == user_id,
                Resume.is_primary == True
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving primary resume for user ID {user_id}: {str(e)}")
            return None

    def set_primary_resume(self, resume_id: int, user_id: int) -> bool:
        """
        Set a resume as the primary resume for a user.

        Args:
            resume_id: ID of the resume to set as primary
            user_id: ID of the user

        Returns:
            True if successful, False otherwise
        """
        try:
            # First, ensure the resume belongs to the user
            resume = self.db.query(Resume).filter(
                Resume.id == resume_id,
                Resume.user_id == user_id
            ).first()

            if not resume:
                return False

            # Reset is_primary flag for all user's resumes
            self.db.query(Resume).filter(
                Resume.user_id == user_id
            ).update({Resume.is_primary: False})

            # Set the specified resume as primary
            resume.is_primary = True
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error setting resume ID {resume_id} as primary for user ID {user_id}: {str(e)}")
            return False

    def get_resumes_by_skills(self, skills: List[str], skip: int = 0, limit: int = 100) -> List[Resume]:
        """
        Find resumes that contain specific skills.

        Args:
            skills: List of skills to match
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Resume instances matching the skills criteria
        """
        try:
            # Using PostgreSQL JSON containment for array items
            resumes = []
            for skill in skills:
                skill_matches = self.db.query(Resume).filter(
                    Resume.skills.contains([skill])
                ).offset(skip).limit(limit).all()

                # Add unique resumes to the result list
                for resume in skill_matches:
                    if resume not in resumes:
                        resumes.append(resume)

                if len(resumes) >= limit:
                    break

            return resumes
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving resumes by skills {skills}: {str(e)}")
            return []

    def update_parsed_content(self, resume_id: int, parsed_content: Dict[str, Any]) -> Optional[Resume]:
        """
        Update the parsed content of a resume.

        Args:
            resume_id: ID of the resume
            parsed_content: Dictionary of parsed resume content

        Returns:
            Updated Resume instance if successful, None otherwise
        """
        try:
            resume = self.get_by_id(resume_id)
            if not resume:
                return None

            resume.parsed_content = parsed_content
            self.db.commit()
            self.db.refresh(resume)
            return resume
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating parsed content for resume ID {resume_id}: {str(e)}")
            return None

    def update_skills(self, resume_id: int, skills: List[str]) -> Optional[Resume]:
        """
        Update the skills extracted from a resume.

        Args:
            resume_id: ID of the resume
            skills: List of skills to set

        Returns:
            Updated Resume instance if successful, None otherwise
        """
        try:
            resume = self.get_by_id(resume_id)
            if not resume:
                return None

            resume.skills = skills
            self.db.commit()
            self.db.refresh(resume)
            return resume
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating skills for resume ID {resume_id}: {str(e)}")
            return None

    def update_experience_and_education(self, resume_id: int, experience: List[Dict], education: List[Dict]) -> \
    Optional[Resume]:
        """
        Update experience and education information for a resume.

        Args:
            resume_id: ID of the resume
            experience: List of dictionaries containing experience information
            education: List of dictionaries containing education information

        Returns:
            Updated Resume instance if successful, None otherwise
        """
        try:
            resume = self.get_by_id(resume_id)
            if not resume:
                return None

            resume.experience = experience
            resume.education = education
            self.db.commit()
            self.db.refresh(resume)
            return resume
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating experience and education for resume ID {resume_id}: {str(e)}")
            return None

    def count_resumes_by_extension(self) -> Dict[str, int]:
        """
        Count resumes by file extension (content type).

        Returns:
            Dictionary with content types as keys and counts as values
        """
        try:
            result = {}
            content_types = self.db.query(
                Resume.content_type,
                func.count(Resume.id)
            ).group_by(Resume.content_type).all()

            for content_type, count in content_types:
                result[content_type] = count

            return result
        except SQLAlchemyError as e:
            logger.error(f"Error counting resumes by extension: {str(e)}")
            return {}