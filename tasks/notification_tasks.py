"""
Notification tasks for sending user notifications about job matches and other events.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from celery import shared_task
import json

from .celery_app import celery_app
from ..database.session import get_db
from ..database.repositories.user_repository import UserRepository
from ..database.repositories.match_repository import MatchRepository
from ..database.repositories.job_repository import JobRepository
from ..services.notifications.notification_service import NotificationService
from ..services.notifications.websocket_manager import WebSocketManager
from ..models.match import Match
from ..models.job import Job
from ..config import get_config

logger = logging.getLogger(__name__)


@shared_task(
    name="tasks.notification_tasks.send_match_notifications",
    bind=True,
    max_retries=2
)
def send_match_notifications(self, hours_back: int = 12, min_score: float = 75):
    """
    Send notifications for new matches created within the specified time period.

    Args:
        hours_back: Hours to look back for new matches
        min_score: Minimum match score to send notifications for

    Returns:
        dict: Summary of the notification results
    """
    logger.info(f"Sending notifications for matches from the last {hours_back} hours with score >= {min_score}")

    try:
        with get_db() as db:
            match_repository = MatchRepository(db)
            user_repository = UserRepository(db)
            job_repository = JobRepository(db)

            # Get notification service
            config = get_config()
            notification_service = NotificationService(config)
            websocket_manager = WebSocketManager()

            # Get recent matches
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            recent_matches = db.query(Match).join(
                Job, Match.job_id == Job.id
            ).filter(
                Match.created_at >= cutoff_time,
                Match.score >= min_score,
                Match.status == 'new',
                Job.is_active == True
            ).all()

            logger.info(f"Found {len(recent_matches)} recent matches to notify users about")

            notifications_sent = 0

            # Process each match
            for match in recent_matches:
                try:
                    # Get user and job details
                    user = user_repository.get_by_id(match.user_id)
                    job = job_repository.get_by_id(match.job_id)

                    if not user or not job:
                        logger.error(f"User {match.user_id} or job {match.job_id} not found for match {match.id}")
                        continue

                    # Format notification message
                    notification_data = {
                        'type': 'new_match',
                        'match_id': match.id,
                        'job_id': job.id,
                        'job_title': job.title,
                        'company': job.company,
                        'match_score': match.score,
                        'timestamp': datetime.utcnow().isoformat()
                    }

                    # Send notification
                    sent = False

                    # Try WebSocket first (real-time if user is online)
                    if websocket_manager.is_connected(user.id):
                        try:
                            websocket_manager.send_message(user.id, json.dumps(notification_data))
                            sent = True
                        except Exception as e:
                            logger.error(f"Error sending WebSocket notification to user {user.id}: {str(e)}")

                    # Fall back to email notification
                    if not sent:
                        notification_service.send_email_notification(
                            user.email,
                            'Novo match de vaga encontrado!',
                            notification_data
                        )

                    # Update match status to 'notified'
                    match_repository.update(match.id, {'status': 'notified'})

                    notifications_sent += 1
                except Exception as e:
                    logger.error(f"Error processing notification for match {match.id}: {str(e)}")
                    continue

            logger.info(f"Sent {notifications_sent} match notifications")

            return {
                "status": "completed",
                "matches_processed": len(recent_matches),
                "notifications_sent": notifications_sent,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error sending match notifications: {str(e)}")
        # Retry the task
        retry_count = self.request.retries
        backoff = 60 * (2 ** retry_count)  # 1 min, 2 min
        raise self.retry(exc=e, countdown=backoff)


@shared_task(
    name="tasks.notification_tasks.send_user_digest",
    bind=True,
    max_retries=2
)
def send_user_digest(self, days_back: int = 3, min_matches: int = 1):
    """
    Send digest emails to users with a summary of their recent matches.

    Args:
        days_back: Days to look back for matches to include in the digest
        min_matches: Minimum number of matches required to send a digest

    Returns:
        dict: Summary of the digest results
    """
    logger.info(f"Preparing user digest emails for matches from the last {days_back} days")

    try:
        with get_db() as db:
            user_repository = UserRepository(db)
            match_repository = MatchRepository(db)

            # Get notification service
            config = get_config()
            notification_service = NotificationService(config)

            # Get active users
            active_users = user_repository.get_active_users()

            logger.info(f"Processing digests for {len(active_users)} active users")

            digests_sent = 0

            # Process each user
            for user in active_users:
                try:
                    # Get user's recent matches
                    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
                    recent_matches = db.query(Match).join(
                        Job, Match.job_id == Job.id
                    ).filter(
                        Match.user_id == user.id,
                        Match.created_at >= cutoff_date,
                        Job.is_active == True
                    ).order_by(
                        Match.score.desc()
                    ).all()

                    # Skip if not enough matches
                    if len(recent_matches) < min_matches:
                        continue

                    # Get match statistics
                    stats = match_repository.get_match_statistics(user.id)

                    # Prepare digest data
                    digest_data = {
                        'user_name': user.name,
                        'match_count': len(recent_matches),
                        'top_matches': [
                            {
                                'job_title': db.query(Job).filter(Job.id == match.job_id).first().title,
                                'company': db.query(Job).filter(Job.id == match.job_id).first().company,
                                'match_score': match.score,
                                'job_id': match.job_id
                            }
                            for match in recent_matches[:5]  # Top 5 matches
                        ],
                        'stats': stats,
                        'date_range': f"{cutoff_date.strftime('%d/%m/%Y')} - {datetime.utcnow().strftime('%d/%m/%Y')}"
                    }

                    # Send digest email
                    notification_service.send_email_digest(
                        user.email,
                        'Resumo semanal de vagas compatíveis',
                        digest_data
                    )

                    digests_sent += 1
                except Exception as e:
                    logger.error(f"Error processing digest for user {user.id}: {str(e)}")
                    continue

            logger.info(f"Sent {digests_sent} user digest emails")

            return {
                "status": "completed",
                "users_processed": len(active_users),
                "digests_sent": digests_sent,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error sending user digests: {str(e)}")
        # Retry the task
        retry_count = self.request.retries
        backoff = 120 * (2 ** retry_count)  # 2 min, 4 min
        raise self.retry(exc=e, countdown=backoff)


@shared_task(
    name="tasks.notification_tasks.send_match_improvement_recommendations",
    bind=True
)
def send_match_improvement_recommendations(self, user_id: int, match_id: int):
    """
    Send recommendations to a user on how to improve their match score for a specific job.

    Args:
        user_id: User ID
        match_id: Match ID

    Returns:
        dict: Summary of the recommendation results
    """
    logger.info(f"Sending match improvement recommendations for user {user_id}, match {match_id}")

    try:
        with get_db() as db:
            user_repository = UserRepository(db)
            match_repository = MatchRepository(db)
            job_repository = JobRepository(db)

            # Get user, match, and job
            user = user_repository.get_by_id(user_id)
            match = match_repository.get_by_id(match_id)

            if not user or not match or match.user_id != user_id:
                logger.error(f"User {user_id} or match {match_id} not found, or match doesn't belong to user")
                return {
                    "status": "error",
                    "error": "User or match not found, or match doesn't belong to user",
                    "user_id": user_id,
                    "match_id": match_id
                }

            job = job_repository.get_by_id(match.job_id)

            if not job:
                logger.error(f"Job {match.job_id} not found for match {match_id}")
                return {
                    "status": "error",
                    "error": "Job not found for match",
                    "match_id": match_id
                }

            # Get notification service
            config = get_config()
            notification_service = NotificationService(config)

            # Extract recommendations from match details
            match_details = match.match_details or {}
            recommendations = match_details.get('recommendations', [])

            if not recommendations:
                logger.info(f"No recommendations available for match {match_id}")
                return {
                    "status": "completed",
                    "user_id": user_id,
                    "match_id": match_id,
                    "message": "No recommendations available",
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Format recommendation message
            recommendation_data = {
                'user_name': user.name,
                'job_title': job.title,
                'company': job.company,
                'match_score': match.score,
                'recommendations': recommendations,
                'match_id': match_id,
                'job_id': job.id
            }

            # Send recommendation email
            notification_service.send_email_recommendation(
                user.email,
                'Recomendações para melhorar sua compatibilidade com a vaga',
                recommendation_data
            )

            logger.info(f"Sent match improvement recommendations to user {user_id} for match {match_id}")

            return {
                "status": "completed",
                "user_id": user_id,
                "match_id": match_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error sending match recommendations: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "user_id": user_id,
            "match_id": match_id,
            "timestamp": datetime.utcnow().isoformat()
        }


@shared_task(
    name="tasks.notification_tasks.notify_new_company_jobs",
    bind=True
)
def notify_new_company_jobs(self, company: str, count: int = 0):
    """
    Notify users who have matches with a company about new job postings.

    Args:
        company: Company name
        count: Number of new jobs

    Returns:
        dict: Summary of the notification results
    """
    logger.info(f"Notifying users about {count} new jobs from {company}")

    try:
        with get_db() as db:
            # Get users who have matches with this company
            users_with_company_matches = db.query(User.id, User.email, User.name).distinct().join(
                Match, User.id == Match.user_id
            ).join(
                Job, Match.job_id == Job.id
            ).filter(
                Job.company.ilike(f"%{company}%"),
                Match.score >= 70  # Only notify users with good matches
            ).all()

            if not users_with_company_matches:
                logger.info(f"No users found with matches for company {company}")
                return {
                    "status": "completed",
                    "company": company,
                    "message": "No users to notify",
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Get notification service
            config = get_config()
            notification_service = NotificationService(config)

            notifications_sent = 0

            # Notify each user
            for user_id, email, name in users_with_company_matches:
                try:
                    # Format notification
                    notification_data = {
                        'user_name': name,
                        'company': company,
                        'job_count': count,
                        'company_url': f"https://www.linkedin.com/company/{company.lower().replace(' ', '-')}/jobs/"
                    }

                    # Send notification email
                    notification_service.send_email_notification(
                        email,
                        f'Novas vagas disponíveis na {company}',
                        notification_data
                    )

                    notifications_sent += 1
                except Exception as e:
                    logger.error(f"Error sending company job notification to user {user_id}: {str(e)}")
                    continue

            logger.info(f"Sent {notifications_sent} notifications about new jobs from {company}")

            return {
                "status": "completed",
                "company": company,
                "job_count": count,
                "users_notified": notifications_sent,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error notifying about new company jobs: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "company": company,
            "timestamp": datetime.utcnow().isoformat()
        }