"""
Job repository for handling job data access operations.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, desc, and_, or_
from datetime import datetime, timedelta
import logging

from .base_repository import BaseRepository
from models.job import Job

logger = logging.getLogger(__name__)


class JobRepository(BaseRepository[Job]):
    """Repository for Job model providing specialized data access operations."""

    def __init__(self, db_session: Session):
        """
        Initialize the Job repository.

        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(Job, db_session)

    def get_by_linkedin_id(self, linkedin_id: str) -> Optional[Job]:
        """
        Get job by LinkedIn ID.

        Args:
            linkedin_id: LinkedIn ID of the job

        Returns:
            Job instance if found, None otherwise
        """
        try:
            return self.db.query(Job).filter(Job.linkedin_id == linkedin_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving job by LinkedIn ID {linkedin_id}: {str(e)}")
            return None

    def save_or_update(self, job_data: Dict[str, Any]) -> Optional[Job]:
        """
        Save a new job or update an existing one based on LinkedIn ID.

        Args:
            job_data: Job data dictionary including linkedin_id

        Returns:
            Created or updated Job instance if successful, None otherwise
        """
        try:
            linkedin_id = job_data.get('linkedin_id')
            if not linkedin_id:
                logger.error("Cannot save job without LinkedIn ID")
                return None

            existing_job = self.get_by_linkedin_id(linkedin_id)

            if existing_job:
                # Update existing job
                for key, value in job_data.items():
                    if hasattr(existing_job, key):
                        setattr(existing_job, key, value)
                existing_job.scraped_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(existing_job)
                return existing_job
            else:
                # Create new job
                return self.create(job_data)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error saving or updating job: {str(e)}")
            return None

    def get_recent_jobs(self, days: int = 7, limit: int = 100) -> List[Job]:
        """
        Get jobs posted within the specified number of days.

        Args:
            days: Number of days to look back
            limit: Maximum number of jobs to return

        Returns:
            List of recent Job instances
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            return self.db.query(Job).filter(
                Job.posted_at >= cutoff_date,
                Job.is_active == True
            ).order_by(desc(Job.posted_at)).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving recent jobs: {str(e)}")
            return []

    def search_jobs(self, keywords: List[str] = None, location: str = None,
                    job_type: str = None, experience_level: str = None,
                    skills: List[str] = None, skip: int = 0, limit: int = 100) -> List[Job]:
        """
        Search for jobs with various filters.

        Args:
            keywords: List of keywords to search in title and description
            location: Location to filter by
            job_type: Job type (full-time, part-time, etc.)
            experience_level: Level of experience required
            skills: List of required skills
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Job instances matching the search criteria
        """
        try:
            query = self.db.query(Job).filter(Job.is_active == True)

            # Apply keyword filters
            if keywords and len(keywords) > 0:
                keyword_filters = []
                for keyword in keywords:
                    keyword_filters.append(Job.title.ilike(f"%{keyword}%"))
                    keyword_filters.append(Job.description.ilike(f"%{keyword}%"))
                    keyword_filters.append(Job.company.ilike(f"%{keyword}%"))

                query = query.filter(or_(*keyword_filters))

            # Apply location filter
            if location:
                query = query.filter(Job.location.ilike(f"%{location}%"))

            # Apply job type filter
            if job_type:
                query = query.filter(Job.job_type == job_type)

            # Apply experience level filter
            if experience_level:
                query = query.filter(Job.experience_level == experience_level)

            # Apply skills filter
            if skills and len(skills) > 0:
                # Assuming skills are stored as a JSON array in PostgreSQL
                for skill in skills:
                    query = query.filter(Job.skills.contains([skill]))

            # Apply pagination and ordering
            return query.order_by(desc(Job.posted_at)).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error searching jobs: {str(e)}")
            return []

    def deactivate_old_jobs(self, days: int = 30) -> int:
        """
        Deactivate jobs that haven't been updated for the specified number of days.

        Args:
            days: Number of days to consider a job as old

        Returns:
            Number of jobs deactivated
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            result = self.db.query(Job).filter(
                Job.scraped_at < cutoff_date,
                Job.is_active == True
            ).update({Job.is_active: False})

            self.db.commit()
            return result
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deactivating old jobs: {str(e)}")
            return 0

    def get_top_companies_by_job_count(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the top companies with the most job listings.

        Args:
            limit: Maximum number of companies to return

        Returns:
            List of dictionaries with company names and job counts
        """
        try:
            result = self.db.query(
                Job.company,
                func.count(Job.id).label('job_count')
            ).filter(
                Job.is_active == True
            ).group_by(Job.company).order_by(desc('job_count')).limit(limit).all()

            return [{'company': company, 'job_count': count} for company, count in result]
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving top companies: {str(e)}")
            return []

    def get_top_skills_in_demand(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get the most in-demand skills based on job listings.

        Args:
            limit: Maximum number of skills to return

        Returns:
            List of dictionaries with skill names and counts
        """
        try:
            # This implementation depends on how skills are stored
            # Assuming skills is a JSON array in PostgreSQL
            # Using PostgreSQL's json array elements function
            result = self.db.query(
                func.jsonb_array_elements_text(Job.skills).label('skill'),
                func.count().label('skill_count')
            ).filter(
                Job.is_active == True
            ).group_by('skill').order_by(desc('skill_count')).limit(limit).all()

            return [{'skill': skill, 'count': count} for skill, count in result]
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving top skills: {str(e)}")
            return []

    def get_job_count_by_experience_level(self) -> Dict[str, int]:
        """
        Get the distribution of jobs by experience level.

        Returns:
            Dictionary with experience levels as keys and counts as values
        """
        try:
            result = {}
            counts = self.db.query(
                Job.experience_level,
                func.count(Job.id)
            ).filter(
                Job.is_active == True
            ).group_by(Job.experience_level).all()

            for level, count in counts:
                result[level] = count

            return result
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving job counts by experience level: {str(e)}")
            return {}

    def get_job_count_by_type(self) -> Dict[str, int]:
        """
        Get the distribution of jobs by job type.

        Returns:
            Dictionary with job types as keys and counts as values
        """
        try:
            result = {}
            counts = self.db.query(
                Job.job_type,
                func.count(Job.id)
            ).filter(
                Job.is_active == True
            ).group_by(Job.job_type).all()

            for job_type, count in counts:
                result[job_type] = count

            return result
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving job counts by job type: {str(e)}")
            return {}