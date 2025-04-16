"""
LinkedIn scraping tasks for job data collection.
"""

import logging
from typing import List
from datetime import datetime, timedelta
from celery import shared_task
from contextlib import contextmanager

from .celery_app import celery_app
from database.session import get_db
from database.repositories.job_repository import JobRepository
from services.scraper.linkedin_scraper import LinkedInScraper
from config import get_config
from services.storage.file_service import FileService

logger = logging.getLogger(__name__)


@contextmanager
def get_scraper():
    """Context manager for LinkedIn scraper."""
    config = get_config()
    scraper = LinkedInScraper(config)
    try:
        scraper.setup_browser()
        yield scraper
    finally:
        scraper.close()


@shared_task(
    name="tasks.scraping_tasks.scheduled_job_scraping",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
    rate_limit="2/h"  # Limit to 2 executions per hour
)
def scheduled_job_scraping(self, keywords: List[str], location: str, pages: int = 5):
    """
    Scheduled task for scraping job listings from LinkedIn.

    Args:
        keywords: List of job keywords to search for
        location: Location to search in
        pages: Number of pages to scrape for each keyword

    Returns:
        dict: Summary of the scraping results
    """
    logger.info(f"Starting scheduled job scraping for keywords: {keywords} in {location}")
    jobs_added = 0
    jobs_updated = 0

    try:
        with get_scraper() as scraper, get_db() as db:
            job_repository = JobRepository(db)

            for keyword in keywords:
                logger.info(f"Scraping jobs for keyword: {keyword}")
                try:
                    # Scrape job listings
                    jobs = scraper.scrape_job_listings(keyword, location, pages=pages)

                    # Process each job
                    for job_data in jobs:
                        # Check if we already have details for this job
                        existing_job = job_repository.get_by_linkedin_id(job_data['linkedin_id'])

                        if existing_job and existing_job.description:
                            # Job already has full details, just update the basic info
                            result = job_repository.save_or_update(job_data)
                            if result:
                                jobs_updated += 1
                        else:
                            # Job is new or missing details, fetch full details
                            try:
                                job_details = scraper.extract_job_details(job_data['url'])
                                # Merge the basic job data with detailed information
                                job_data.update(job_details)
                                result = job_repository.save_or_update(job_data)

                                if result:
                                    if existing_job:
                                        jobs_updated += 1
                                    else:
                                        jobs_added += 1
                            except Exception as e:
                                logger.error(f"Error extracting details for job {job_data['linkedin_id']}: {str(e)}")
                except Exception as e:
                    logger.error(f"Error scraping jobs for keyword {keyword}: {str(e)}")
                    continue
    except Exception as e:
        logger.error(f"Error in scheduled job scraping: {str(e)}")
        # Retry the task with exponential backoff
        retry_count = self.request.retries
        backoff = 300 * (2 ** retry_count)  # 5 min, 10 min, 20 min
        raise self.retry(exc=e, countdown=backoff)

    logger.info(f"Scheduled job scraping completed: {jobs_added} jobs added, {jobs_updated} jobs updated")

    return {
        "status": "completed",
        "jobs_added": jobs_added,
        "jobs_updated": jobs_updated,
        "keywords": keywords,
        "location": location,
        "timestamp": datetime.utcnow().isoformat()
    }


@shared_task(
    name="tasks.scraping_tasks.scheduled_post_scraping",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
    rate_limit="1/h"  # Limit to 1 execution per hour
)
def scheduled_post_scraping(self, keywords: List[str], days_back: int = 3, max_posts: int = 100):
    """
    Scheduled task for scraping LinkedIn posts that contain job listings.

    Args:
        keywords: List of keywords to search for in posts
        days_back: Number of days to look back for posts
        max_posts: Maximum number of posts to scrape

    Returns:
        dict: Summary of the scraping results
    """
    logger.info(f"Starting scheduled post scraping for keywords: {keywords}, looking back {days_back} days")
    posts_scraped = 0
    jobs_extracted = 0

    config = get_config()

    try:
        with get_scraper() as scraper, get_db() as db:
            job_repository = JobRepository(db)

            # Login required for post scraping
            scraper.login(config.LINKEDIN_USERNAME, config.LINKEDIN_PASSWORD)

            for keyword in keywords:
                logger.info(f"Scraping posts for keyword: {keyword}")
                try:
                    # Scrape posts
                    posts = scraper.scrape_posts(keyword, days_back=days_back, max_posts=max_posts // len(keywords))
                    posts_scraped += len(posts)

                    # Process each post
                    for post_data in posts:
                        try:
                            # Extract job information from post
                            job_data = scraper.parse_job_from_post(post_data)

                            if job_data:
                                # Generate a unique LinkedIn ID if not available
                                if 'linkedin_id' not in job_data:
                                    post_id = post_data.get('id', '')
                                    job_data['linkedin_id'] = f"post_{post_id}_{job_data['company']}"

                                # Add source information
                                job_data['source'] = 'linkedin_post'
                                job_data['source_url'] = post_data.get('url', '')
                                job_data['posted_at'] = post_data.get('posted_at', datetime.utcnow())

                                # Save or update the job
                                result = job_repository.save_or_update(job_data)

                                if result:
                                    jobs_extracted += 1
                        except Exception as e:
                            logger.error(f"Error parsing job from post: {str(e)}")
                            continue
                except Exception as e:
                    logger.error(f"Error scraping posts for keyword {keyword}: {str(e)}")
                    continue
    except Exception as e:
        logger.error(f"Error in scheduled post scraping: {str(e)}")
        # Retry the task with exponential backoff
        retry_count = self.request.retries
        backoff = 300 * (2 ** retry_count)  # 5 min, 10 min, 20 min
        raise self.retry(exc=e, countdown=backoff)

    logger.info(f"Scheduled post scraping completed: {posts_scraped} posts scraped, {jobs_extracted} jobs extracted")

    return {
        "status": "completed",
        "posts_scraped": posts_scraped,
        "jobs_extracted": jobs_extracted,
        "keywords": keywords,
        "days_back": days_back,
        "timestamp": datetime.utcnow().isoformat()
    }


@shared_task(
    name="tasks.scraping_tasks.deactivate_old_jobs",
    bind=True
)
def deactivate_old_jobs(self, days: int = 30):
    """
    Scheduled task to deactivate jobs that haven't been updated for a specified period.

    Args:
        days: Number of days after which jobs are considered old

    Returns:
        dict: Summary of the deactivation results
    """
    logger.info(f"Starting deactivation of jobs older than {days} days")

    try:
        with get_db() as db:
            job_repository = JobRepository(db)
            count = job_repository.deactivate_old_jobs(days)

            logger.info(f"Deactivated {count} old jobs")

            return {
                "status": "completed",
                "deactivated_count": count,
                "days_threshold": days,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error deactivating old jobs: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@shared_task(
    name="tasks.scraping_tasks.refresh_job_details",
    bind=True,
    max_retries=2
)
def refresh_job_details(self, job_id: int):
    """
    Task to refresh the details of a specific job.

    Args:
        job_id: ID of the job to refresh

    Returns:
        dict: Summary of the refresh results
    """
    logger.info(f"Refreshing details for job ID: {job_id}")

    try:
        with get_scraper() as scraper, get_db() as db:
            job_repository = JobRepository(db)
            job = job_repository.get_by_id(job_id)

            if not job or not job.url:
                logger.error(f"Job ID {job_id} not found or missing URL")
                return {
                    "status": "error",
                    "error": "Job not found or missing URL",
                    "job_id": job_id
                }

            # Extract updated job details
            job_details = scraper.extract_job_details(job.url)

            # Update the job
            update_data = {
                'description': job_details.get('description', job.description),
                'requirements': job_details.get('requirements', job.requirements),
                'skills': job_details.get('skills', job.skills),
                'scraped_at': datetime.utcnow()
            }

            updated_job = job_repository.update(job_id, update_data)

            if updated_job:
                logger.info(f"Successfully refreshed details for job ID: {job_id}")
                return {
                    "status": "completed",
                    "job_id": job_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"Failed to update job ID: {job_id}")
                return {
                    "status": "error",
                    "error": "Failed to update job",
                    "job_id": job_id
                }
    except Exception as e:
        logger.error(f"Error refreshing job details for job ID {job_id}: {str(e)}")
        # Retry the task
        retry_count = self.request.retries
        backoff = 60 * (2 ** retry_count)  # 1 min, 2 min
        raise self.retry(exc=e, countdown=backoff)


@shared_task(
    name="tasks.scraping_tasks.scrape_company_jobs",
    bind=True,
    max_retries=2
)
def scrape_company_jobs(self, company_name: str, pages: int = 3):
    """
    Task to scrape jobs for a specific company.

    Args:
        company_name: Name of the company to scrape jobs for
        pages: Number of pages to scrape

    Returns:
        dict: Summary of the scraping results
    """
    logger.info(f"Scraping jobs for company: {company_name}")
    jobs_added = 0
    jobs_updated = 0

    try:
        with get_scraper() as scraper, get_db() as db:
            job_repository = JobRepository(db)

            # Scrape company jobs
            jobs = scraper.scrape_company_jobs(company_name, pages=pages)

            # Process each job
            for job_data in jobs:
                existing_job = job_repository.get_by_linkedin_id(job_data['linkedin_id'])

                if existing_job and existing_job.description:
                    # Update basic info
                    result = job_repository.save_or_update(job_data)
                    if result:
                        jobs_updated += 1
                else:
                    # Fetch full details
                    try:
                        job_details = scraper.extract_job_details(job_data['url'])
                        job_data.update(job_details)
                        result = job_repository.save_or_update(job_data)

                        if result:
                            if existing_job:
                                jobs_updated += 1
                            else:
                                jobs_added += 1
                    except Exception as e:
                        logger.error(f"Error extracting details for job {job_data['linkedin_id']}: {str(e)}")

            logger.info(
                f"Completed scraping jobs for company {company_name}: {jobs_added} added, {jobs_updated} updated")

            return {
                "status": "completed",
                "company": company_name,
                "jobs_added": jobs_added,
                "jobs_updated": jobs_updated,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Error scraping jobs for company {company_name}: {str(e)}")
        # Retry the task
        retry_count = self.request.retries
        backoff = 120 * (2 ** retry_count)  # 2 min, 4 min
        raise self.retry(exc=e, countdown=backoff)