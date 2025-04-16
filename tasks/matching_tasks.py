"""
Matching tasks for job-resume matching and analysis.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from celery import shared_task
from sqlalchemy import and_, func

from .celery_app import celery_app
from ..database.session import get_db
from ..database.repositories.job_repository import JobRepository
from ..database.repositories.resume_repository import ResumeRepository
from ..database.repositories.user_repository import UserRepository
from ..database.repositories.match_repository import MatchRepository
from ..services.matching.match_service import MatchService
from ..services.ai.claude_service import ClaudeService
from ..config import get_config

logger = logging.getLogger(__name__)


@shared_task(
    name="tasks.matching_tasks.process_new_jobs_matching",
    bind=True,
    max_retries=3,
    rate_limit="6/h"  # Limit to 6 executions per hour
)
def process_new_jobs_matching(self, days: int = 1, batch_size: int = 50):
    """
    Process new jobs to find matches for existing users with resumes.

    Args:
        days: Number of days to look back for new jobs
        batch_size: Number of jobs to process in one batch

    Returns:
        dict: Summary of the matching results
    """
    logger.info(f"Starting matching for jobs from the last {days} days")

    try:
        with get_db() as db:
            job_repository = JobRepository(db)
            user_repository = UserRepository(db)
            resume_repository = ResumeRepository(db)
            match_repository = MatchRepository(db)

            # Get the AI service
            config = get_config()
            claude_service = ClaudeService(config.CLAUDE_API_KEY)
            match_service = MatchService(claude_service)

            # Get recent jobs
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            recent_jobs = job_repository.db.query(Job).filter(
                and_(
                    Job.scraped_at >= cutoff_date,
                    Job.is_active == True
                )
            ).limit(batch_size).all()

            logger.info(f"Found {len(recent_jobs)} jobs to process")

            # Get users with resumes
            users_with_resumes = user_repository.get_users_with_resumes()

            total_matches_created = 0

            # Process each job
            for job in recent_jobs:
                for user in users_with_resumes:
                    # Get the user's primary resume
                    resume = resume_repository.get_primary_resume(user.id)

                    if not resume:
                        continue

                    # Check if we already have a match for this job-user pair
                    existing_match = match_repository.get_match_by_user_and_job(user.id, job.id)

                    if existing_match:
                        continue

                    # Calculate match score
                    try:
                        match_result = match_service.calculate_match(resume, job)

                        # Create the match record
                        match_data = {
                            'user_id': user.id,
                            'job_id': job.id,
                            'resume_id': resume.id,
                            'score': match_result['score'],
                            'match_details': match_result['details'],
                            'status': 'new'
                        }

                        match = match_repository.create(match_data)

                        if match:
                            total_matches_created += 1
                    except Exception as e:
                        logger.error(f"Error calculating match for user {user.id} and job {job.id}: {str(e)}")
                        continue

            logger.info(f"Created {total_matches_created} new matches")

            return {
                "status": "completed",
                "jobs_processed": len(recent_jobs),
                "users_processed": len(users_with_resumes),
                "matches_created": total_matches_created,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error processing new jobs matching: {str(e)}")
        # Retry the task with exponential backoff
        retry_count = self.request.retries
        backoff = 300 * (2 ** retry_count)  # 5 min, 10 min, 20 min
        raise self.retry(exc=e, countdown=backoff)


@shared_task(
    name="tasks.matching_tasks.process_resume_matching",
    bind=True,
    max_retries=2
)
def process_resume_matching(self, user_id: int, resume_id: int, max_jobs: int = 100):
    """
    Process a specific resume to find matching jobs.

    Args:
        user_id: User ID
        resume_id: Resume ID to process
        max_jobs: Maximum number of jobs to match against

    Returns:
        dict: Summary of the matching results
    """
    logger.info(f"Processing resume matching for user {user_id}, resume {resume_id}")

    try:
        with get_db() as db:
            job_repository = JobRepository(db)
            resume_repository = ResumeRepository(db)
            match_repository = MatchRepository(db)

            # Get the resume
            resume = resume_repository.get_by_id(resume_id)

            if not resume or resume.user_id != user_id:
                logger.error(f"Resume {resume_id} not found or doesn't belong to user {user_id}")
                return {
                    "status": "error",
                    "error": "Resume not found or doesn't belong to user",
                    "user_id": user_id,
                    "resume_id": resume_id
                }

            # Get the AI service
            config = get_config()
            claude_service = ClaudeService(config.CLAUDE_API_KEY)
            match_service = MatchService(claude_service)

            # Get active jobs, prioritizing recent ones
            active_jobs = job_repository.db.query(Job).filter(
                Job.is_active == True
            ).order_by(
                Job.posted_at.desc()
            ).limit(max_jobs).all()

            logger.info(f"Found {len(active_jobs)} active jobs to match against")

            matches_created = 0
            matches_updated = 0

            # Process each job
            for job in active_jobs:
                existing_match = match_repository.get_match_by_user_and_job(user_id, job.id)

                try:
                    # Calculate match score
                    match_result = match_service.calculate_match(resume, job)

                    if existing_match:
                        # Update existing match
                        updated = match_repository.update(existing_match.id, {
                            'resume_id': resume_id,
                            'score': match_result['score'],
                            'match_details': match_result['details']
                        })

                        if updated:
                            matches_updated += 1
                    else:
                        # Create new match
                        match_data = {
                            'user_id': user_id,
                            'job_id': job.id,
                            'resume_id': resume_id,
                            'score': match_result['score'],
                            'match_details': match_result['details'],
                            'status': 'new'
                        }

                        match = match_repository.create(match_data)

                        if match:
                            matches_created += 1
                except Exception as e:
                    logger.error(f"Error calculating match for resume {resume_id} and job {job.id}: {str(e)}")
                    continue

            logger.info(f"Created {matches_created} new matches, updated {matches_updated} existing matches")

            return {
                "status": "completed",
                "user_id": user_id,
                "resume_id": resume_id,
                "jobs_processed": len(active_jobs),
                "matches_created": matches_created,
                "matches_updated": matches_updated,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error processing resume matching: {str(e)}")
        # Retry the task
        retry_count = self.request.retries
        backoff = 60 * (2 ** retry_count)  # 1 min, 2 min
        raise self.retry(exc=e, countdown=backoff)


@shared_task(
    name="tasks.matching_tasks.update_match_scores",
    bind=True,
    max_retries=2,
    time_limit=7200  # 2 hour time limit
)
def update_match_scores(self, batch_size: int = 500, min_age_days: int = 7):
    """
    Update match scores for existing matches that are older than a specified threshold.

    Args:
        batch_size: Number of matches to update in one batch
        min_age_days: Minimum age in days for matches to be updated

    Returns:
        dict: Summary of the update results
    """
    logger.info(f"Starting update of match scores for matches older than {min_age_days} days")

    try:
        with get_db() as db:
            match_repository = MatchRepository(db)
            job_repository = JobRepository(db)
            resume_repository = ResumeRepository(db)

            # Get the AI service
            config = get_config()
            claude_service = ClaudeService(config.CLAUDE_API_KEY)
            match_service = MatchService(claude_service)

            # Get old matches
            cutoff_date = datetime.utcnow() - timedelta(days=min_age_days)
            old_matches = match_repository.db.query(Match).filter(
                Match.created_at <= cutoff_date
            ).limit(batch_size).all()

            logger.info(f"Found {len(old_matches)} old matches to update")

            matches_updated = 0
            errors = 0

            # Process each match
            for match in old_matches:
                try:
                    # Get the resume and job
                    resume = resume_repository.get_by_id(match.resume_id)
                    job = job_repository.get_by_id(match.job_id)

                    if not resume or not job:
                        logger.error(
                            f"Could not find resume {match.resume_id} or job {match.job_id} for match {match.id}")
                        continue

                    # Recalculate match score
                    match_result = match_service.calculate_match(resume, job)

                    # Update the match
                    updated = match_repository.update(match.id, {
                        'score': match_result['score'],
                        'match_details': match_result['details']
                    })

                    if updated:
                        matches_updated += 1
                except Exception as e:
                    logger.error(f"Error updating match {match.id}: {str(e)}")
                    errors += 1
                    continue

            logger.info(f"Updated {matches_updated} matches, encountered {errors} errors")

            return {
                "status": "completed",
                "matches_processed": len(old_matches),
                "matches_updated": matches_updated,
                "errors": errors,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error updating match scores: {str(e)}")
        # Retry the task
        retry_count = self.request.retries
        backoff = 300 * (2 ** retry_count)  # 5 min, 10 min
        raise self.retry(exc=e, countdown=backoff)


@shared_task(
    name="tasks.matching_tasks.generate_job_recommendations",
    bind=True
)
def generate_job_recommendations(self, user_id: int, count: int = 10):
    """
    Generate personalized job recommendations for a user.

    Args:
        user_id: User ID to generate recommendations for
        count: Number of recommendations to generate

    Returns:
        dict: Summary of the recommendation results
    """
    logger.info(f"Generating job recommendations for user {user_id}")

    try:
        with get_db() as db:
            user_repository = UserRepository(db)
            resume_repository = ResumeRepository(db)
            job_repository = JobRepository(db)
            match_repository = MatchRepository(db)

            # Get the user's primary resume
            resume = resume_repository.get_primary_resume(user_id)

            if not resume:
                logger.error(f"User {user_id} has no primary resume")
                return {
                    "status": "error",
                    "error": "User has no primary resume",
                    "user_id": user_id
                }

            # Get the AI service
            config = get_config()
            claude_service = ClaudeService(config.CLAUDE_API_KEY)
            match_service = MatchService(claude_service)

            # Extract user preferences from profile or past interactions
            user = user_repository.get_by_id(user_id)
            if not user or not user.profile:
                logger.error(f"User {user_id} not found or has no profile")
                return {
                    "status": "error",
                    "error": "User not found or has no profile",
                    "user_id": user_id
                }

            # Get user's preferences
            preferences = user.profile.job_preferences or {}
            preferred_skills = resume.skills or []

            # Find jobs that match user preferences but haven't been matched yet
            recommended_jobs = match_service.find_recommended_jobs(
                user_id=user_id,
                resume=resume,
                preferences=preferences,
                preferred_skills=preferred_skills,
                count=count
            )

            # Create matches for the recommended jobs
            recommendations_created = 0

            for job in recommended_jobs:
                # Check if we already have a match
                existing_match = match_repository.get_match_by_user_and_job(user_id, job.id)

                if existing_match:
                    continue

                # Calculate match score
                try:
                    match_result = match_service.calculate_match(resume, job)

                    # Create the match
                    match_data = {
                        'user_id': user_id,
                        'job_id': job.id,
                        'resume_id': resume.id,
                        'score': match_result['score'],
                        'match_details': match_result['details'],
                        'status': 'recommended'  # Special status for recommendations
                    }

                    match = match_repository.create(match_data)

                    if match:
                        recommendations_created += 1
                except Exception as e:
                    logger.error(f"Error creating recommendation for user {user_id} and job {job.id}: {str(e)}")
                    continue

            logger.info(f"Created {recommendations_created} job recommendations for user {user_id}")

            return {
                "status": "completed",
                "user_id": user_id,
                "recommendations_created": recommendations_created,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error generating job recommendations: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }