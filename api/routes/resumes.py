"""
Resume routes for the API.

This module defines the routes for resume operations,
including upload, retrieval, and analysis.
"""
from flask_restful import Api

from ..controllers.resume_controller import (
    ResumeResource,
    ResumeUploadResource
)


def register_resume_routes(api: Api):
    """Register resume related routes.

    Args:
        api: Flask-RESTful API instance
    """
    api.add_resource(ResumeResource, '/resume')
    api.add_resource(ResumeUploadResource, '/resume/upload')