"""
Match repository for handling match data access operations.
"""

from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, desc, and_, or_
import logging

from .base_repository import BaseRepository
from models.match import Match

logger = logging.getLogger(__name__)


class MatchRepository(BaseRepository[Match]):
    """Repository for Match model providing specialized data access operations."""

    def __init__(self, db_session: Session):
        """
        Initialize the Match repository.

        Args:
            db_session: SQLAlchemy database session
        """
        super().__init__(Match, db_session)

    def get_user_matches(self, user_id: int, min_score: float = 0,
                         status: str = None, skip: int = 0, limit: int = 100) -> List[Match]:
        """
        Get matches for a specific user with optional filters.

        Args:
            user_id: ID of the user
            min_score: Minimum match score to include (0-100)
            status: Filter by match status (e.g., 'new', 'viewed', 'applied')
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Match instances for the user
        """
        try:
            query = self.db.query(Match).filter(
                Match.user_id == user_id,
                Match.score >= min_score
            )

            if status:
                query = query.filter(Match.status == status)

            return query.order_by(desc(Match.score), desc(Match.created_at)).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving matches for user ID {user_id}: {str(e)}")
            return []

    def get_match_by_user_and_job(self, user_id: int, job_id: int) -> Optional[Match]:
        """
        Get a specific match between a user and a job.

        Args:
            user_id: ID of the user
            job_id: ID of the job

        Returns:
            Match instance if found, None otherwise
        """
        try:
            return self.db.query(Match).filter(
                Match.user_id == user_id,
                Match.job_id == job_id
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving match for user ID {user_id} and job ID {job_id}: {str(e)}")
            return None

    def create_or_update_match(self, user_id: int, job_id: int, resume_id: int,
                               score: float, match_details: Dict[str, Any]) -> Optional[Match]:
        """
        Create a new match or update an existing one.

        Args:
            user_id: ID of the user
            job_id: ID of the job
            resume_id: ID of the resume used for matching
            score: Match score (0-100)
            match_details: Dictionary with detailed match information

        Returns:
            Created or updated Match instance if successful, None otherwise
        """
        try:
            existing_match = self.get_match_by_user_and_job(user_id, job_id)

            if existing_match:
                # Update existing match
                existing_match.resume_id = resume_id
                existing_match.score = score
                existing_match.match_details = match_details
                self.db.commit()
                self.db.refresh(existing_match)
                return existing_match
            else:
                # Create new match
                match_data = {
                    'user_id': user_id,
                    'job_id': job_id,
                    'resume_id': resume_id,
                    'score': score,
                    'match_details': match_details,
                    'status': 'new'
                }
                return self.create(match_data)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating or updating match for user ID {user_id} and job ID {job_id}: {str(e)}")
            return None

    def update_match_status(self, match_id: int, status: str) -> bool:
        """
        Update the status of a match.

        Args:
            match_id: ID of the match
            status: New status (e.g., 'new', 'viewed', 'applied', 'interviewed', 'rejected', 'accepted')

        Returns:
            True if successful, False otherwise
        """
        try:
            match = self.get_by_id(match_id)
            if not match:
                return False

            match.status = status
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating status for match ID {match_id}: {str(e)}")
            return False

    def batch_create_matches(self, matches_data: List[Dict[str, Any]]) -> int:
        """
        Create multiple matches in batch.

        Args:
            matches_data: List of match data dictionaries

        Returns:
            Number of matches successfully created
        """
        try:
            matches = [Match(**match_data) for match_data in matches_data]
            self.db.add_all(matches)
            self.db.commit()
            return len(matches)
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error batch creating matches: {str(e)}")
            return 0

    def get_top_matches_for_job(self, job_id: int, min_score: float = 70, limit: int = 20) -> List[Tuple[Match, str]]:
        """
        Get the top user matches for a specific job.

        Args:
            job_id: ID of the job
            min_score: Minimum match score to include
            limit: Maximum number of matches to return

        Returns:
            List of tuples containing Match instances and user names
        """
        try:
            # This query joins Match with User to get the user name
            result = self.db.query(
                Match,
                User.name
            ).join(
                User, Match.user_id == User.id
            ).filter(
                Match.job_id == job_id,
                Match.score >= min_score
            ).order_by(
                desc(Match.score)
            ).limit(limit).all()

            return result
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving top matches for job ID {job_id}: {str(e)}")
            return []

    def get_match_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Get match statistics for a user.

        Args:
            user_id: ID of the user

        Returns:
            Dictionary with match statistics
        """
        try:
            # Count matches by score range
            score_ranges = {
                'excellent': self.db.query(func.count(Match.id)).filter(
                    Match.user_id == user_id,
                    Match.score >= 85
                ).scalar() or 0,

                'good': self.db.query(func.count(Match.id)).filter(
                    Match.user_id == user_id,
                    Match.score >= 70,
                    Match.score < 85
                ).scalar() or 0,

                'average': self.db.query(func.count(Match.id)).filter(
                    Match.user_id == user_id,
                    Match.score >= 50,
                    Match.score < 70
                ).scalar() or 0,

                'low': self.db.query(func.count(Match.id)).filter(
                    Match.user_id == user_id,
                    Match.score < 50
                ).scalar() or 0
            }

            # Count matches by status
            status_counts = {}
            statuses = self.db.query(
                Match.status,
                func.count(Match.id)
            ).filter(
                Match.user_id == user_id
            ).group_by(Match.status).all()

            for status, count in statuses:
                status_counts[status] = count

            # Calculate average match score
            avg_score = self.db.query(
                func.avg(Match.score)
            ).filter(
                Match.user_id == user_id
            ).scalar() or 0

            # Get total match count
            total_matches = self.db.query(
                func.count(Match.id)
            ).filter(
                Match.user_id == user_id
            ).scalar() or 0

            return {
                'total_matches': total_matches,
                'score_ranges': score_ranges,
                'status_counts': status_counts,
                'average_score': round(avg_score, 2)
            }
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving match statistics for user ID {user_id}: {str(e)}")
            return {
                'total_matches': 0,
                'score_ranges': {'excellent': 0, 'good': 0, 'average': 0, 'low': 0},
                'status_counts': {},
                'average_score': 0
            }