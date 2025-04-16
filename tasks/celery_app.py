"""
Celery configuration for LinkedIn Job Matcher.
"""

import os
from celery import Celery
from celery.schedules import crontab
from flask import Flask

# Configure Celery
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

def make_celery(app=None):
    """
    Create and configure a Celery instance that can be used with Flask application.

    If a Flask app is provided, the Celery instance will be configured to use
    the Flask application context.

    Args:
        app: Optional Flask application instance

    Returns:
        Configured Celery instance
    """
    celery_instance = Celery(
        'linkedin_job_matcher',
        broker=REDIS_URL,
        backend=REDIS_URL,
        include=[
            'tasks.scraping_tasks',
            'tasks.matching_tasks',
            'tasks.notification_tasks'
        ]
    )

    # Configure Celery
    celery_instance.conf.update(
        # Task settings
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,

        # Task execution settings
        task_acks_late=True,  # Tasks are acknowledged after execution, not before
        task_reject_on_worker_lost=True,  # Requeue tasks that were being executed on a worker that was terminated
        worker_prefetch_multiplier=1,  # Prefetch 1 task at a time

        # Task result settings
        task_ignore_result=False,  # Store task results
        result_expires=60 * 60 * 24 * 3,  # Results expire after 3 days

        # Retry settings
        task_default_retry_delay=300,  # 5 minutes
        task_max_retries=3,  # Retry failed tasks 3 times

        # Rate limiting
        task_default_rate_limit='10/m',  # Default to 10 tasks per minute per worker

        # Log settings
        worker_redirect_stdouts=False,  # Don't redirect stdout/stderr
        worker_log_color=True,  # Enable colorized logging

        # Schedule periodic tasks
        beat_schedule={
            'scrape-job-listings': {
                'task': 'tasks.scraping_tasks.scheduled_job_scraping',
                'schedule': crontab(hour='*/2', minute='0'),  # Every 2 hours
                'args': (['python', 'data engineer', 'machine learning', 'software engineer', 'developer'], 'Brazil'),
                'options': {'expires': 3600}  # Task expires after 1 hour
            },
            'scrape-linkedin-posts': {
                'task': 'tasks.scraping_tasks.scheduled_post_scraping',
                'schedule': crontab(hour='*/4', minute='30'),  # Every 4 hours
                'args': (['estamos contratando', 'vaga aberta', 'oportunidade', 'job opening'], 3),
                'options': {'expires': 3600}  # Task expires after 1 hour
            },
            'process-new-jobs-matching': {
                'task': 'tasks.matching_tasks.process_new_jobs_matching',
                'schedule': crontab(hour='*/3', minute='15'),  # Every 3 hours
                'options': {'expires': 3600}  # Task expires after 1 hour
            },
            'update-match-scores': {
                'task': 'tasks.matching_tasks.update_match_scores',
                'schedule': crontab(day_of_week='monday', hour='3', minute='0'),  # Every Monday at 3 AM
                'options': {'expires': 14400}  # Task expires after 4 hours
            },
            'send-match-notifications': {
                'task': 'tasks.notification_tasks.send_match_notifications',
                'schedule': crontab(hour='9,15', minute='0'),  # At 9 AM and 3 PM
                'options': {'expires': 3600}  # Task expires after 1 hour
            },
            'send-user-digest': {
                'task': 'tasks.notification_tasks.send_user_digest',
                'schedule': crontab(day_of_week='monday,thursday', hour='10', minute='0'),  # Mon & Thu at 10 AM
                'options': {'expires': 7200}  # Task expires after 2 hours
            },
            'deactivate-old-jobs': {
                'task': 'tasks.scraping_tasks.deactivate_old_jobs',
                'schedule': crontab(day_of_week='sunday', hour='1', minute='0'),  # Every Sunday at 1 AM
                'options': {'expires': 3600}  # Task expires after 1 hour
            }
        }
    )

    # Optional configuration for testing
    celery_instance.conf.update(
        task_always_eager=os.getenv('CELERY_TASK_ALWAYS_EAGER', 'false').lower() == 'true'
    )

    # If a Flask app is provided, integrate Celery with Flask application context
    if app:
        class FlaskTask(celery_instance.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery_instance.Task = FlaskTask

    return celery_instance

# Create a default Celery instance without Flask app
celery_app = make_celery()

# If this file is executed directly, start the Celery worker
if __name__ == '__main__':
    celery_app.start()