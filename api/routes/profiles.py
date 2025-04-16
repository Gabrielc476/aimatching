"""
Profile routes for the API.

This module defines the routes for user profile operations,
including retrieving and updating profile information.
"""
from flask_restful import Api

from ..controllers.profile_controller import ProfileResource


def register_profile_routes(api: Api):
    """Register profile related routes.

    Args:
        api: Flask-RESTful API instance
    """
    api.add_resource(ProfileResource, '/profile')