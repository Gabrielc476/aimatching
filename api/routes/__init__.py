"""
Routes module for the API.

This module manages the registration of all API routes and resources.
"""
from flask_restful import Api

from .auth import register_auth_routes
from .jobs import register_job_routes
from .profiles import register_profile_routes
from .resumes import register_resume_routes
from .matches import register_match_routes


def register_routes(api: Api):
    """Register all API routes with the given API instance.

    Args:
        api: Flask-RESTful API instance
    """
    # Register routes for each module
    register_auth_routes(api)
    register_job_routes(api)
    register_profile_routes(api)
    register_resume_routes(api)
    register_match_routes(api)