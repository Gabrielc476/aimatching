"""
Job controller for the API.

This module provides controller classes for handling job-related requests,
including listing, retrieving details, searching, and finding matching jobs.
"""
from flask import request, current_app
from flask_jwt_extended import jwt_required

from . import BaseController
from ..middlewares.auth import jwt_required
from ..schemas.jobs import (
    job_schema,
    jobs_schema,
    job_list_schema,
    job_search_schema
)
from database.repositories.job_repository import JobRepository
from database.repositories.match_repository import MatchRepository
from services.matching.match_service import MatchService


class JobListResource(BaseController):
    """Resource for listing jobs."""

    def __init__(self):
        """Initialize the job list resource."""
        self.job_repository = JobRepository()

    def get(self):
        """Get a list of jobs.

        Returns:
            tuple: Response data and status code
        """
        page, per_page = self._get_pagination_params()

        # Get jobs with pagination
        jobs, total, total_pages = self.job_repository.get_paginated(
            page=page,
            per_page=per_page,
            is_active=True
        )

        # Prepare response
        response_data = {
            'jobs': jobs_schema.dump(jobs),
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }

        return self._success_response(data=response_data)


class JobDetailResource(BaseController):
    """Resource for retrieving job details."""

    def __init__(self):
        """Initialize the job detail resource."""
        self.job_repository = JobRepository()

    def get(self, job_id):
        """Get details of a specific job.

        Args:
            job_id: ID of the job

        Returns:
            tuple: Response data and status code
        """
        job = self.job_repository.get_by_id(job_id)

        if not job:
            return self._error_response(
                "Job not found",
                status_code=404
            )

        return self._success_response(data=job_schema.dump(job))


class JobSearchResource(BaseController):
    """Resource for searching jobs."""

    def __init__(self):
        """Initialize the job search resource."""
        self.job_repository = JobRepository()

    def post(self):
        """Search for jobs based on criteria.

        Returns:
            tuple: Response data and status code
        """
        search_params = self._validate_schema(job_search_schema, request.json)
        page, per_page = search_params.pop('page', 1), search_params.pop('per_page', 20)

        # Search jobs with pagination
        jobs, total, total_pages = self.job_repository.search(
            **search_params,
            page=page,
            per_page=per_page,
            is_active=True
        )

        # Prepare response
        response_data = {
            'jobs': jobs_schema.dump(jobs),
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }

        return self._success_response(data=response_data)


class JobMatchesResource(BaseController):
    """Resource for finding jobs that match the user's profile."""

    def __init__(self):
        """Initialize the job matches resource."""
        self.match_repository = MatchRepository()
        self.match_service = MatchService()

    @jwt_required
    def get(self):
        """Get jobs that match the user's profile.

        Returns:
            tuple: Response data and status code
        """
        user = self._get_current_user()
        page, per_page = self._get_pagination_params()

        # Get matches for the user with pagination
        matches, total, total_pages = self.match_repository.get_user_matches(
            user_id=user.id,
            page=page,
            per_page=per_page
        )

        # Check if matches exist
        if not matches and page == 1:
            # Queue a task to generate matches
            from tasks.matching_tasks import generate_user_matches
            generate_user_matches.delay(user.id)

            return self._success_response(
                data={
                    'matches': [],
                    'total': 0,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': 0
                },
                message="Matching jobs are being generated. Please check back soon."
            )

        # Prepare response
        response_data = {
            'matches': [
                {
                    'job': job_schema.dump(match.job),
                    'score': match.score,
                    'match_details': match.match_details
                }
                for match in matches
            ],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }

        return self._success_response(data=response_data)