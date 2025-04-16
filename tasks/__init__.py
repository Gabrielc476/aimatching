"""
Tasks package for LinkedIn Job Matcher.
This package handles asynchronous and scheduled tasks using Celery.
"""

from .celery_app import celery_app
from .scraping_tasks import scheduled_job_scraping, scheduled_post_scraping
from .matching_tasks import process_new_jobs_matching, process_resume_matching, update_match_scores
from .notification_tasks import send_match_notifications, send_user_digest

__all__ = [
    'celery_app',
    'scheduled_job_scraping',
    'scheduled_post_scraping',
    'process_new_jobs_matching',
    'process_resume_matching',
    'update_match_scores',
    'send_match_notifications',
    'send_user_digest'
]