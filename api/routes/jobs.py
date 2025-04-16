"""
Job routes for the API.

This module defines the routes for job-related operations, including
listing, retrieving details, searching, and finding matching jobs.
"""
from flask_restful import Api

from ..controllers.job_controller import (
    JobListResource,
    JobDetailResource,
    JobSearchResource,
    JobMatchesResource
)


def register_job_routes(api: Api):
    """Register job related routes.

    Args:
        api: Flask-RESTful API instance
    """
    api.add_resource(JobListResource, '/jobs')
    api.add_resource(JobDetailResource, '/jobs/<int:job_id>')
    api.add_resource(JobSearchResource, '/jobs/search')
    api.add_resource(JobMatchesResource, '/jobs/matches')