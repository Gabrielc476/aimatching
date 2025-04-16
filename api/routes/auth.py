"""
Authentication routes for the API.

This module defines the routes for user authentication, including
registration, login, token refresh, and logout.
"""
from flask_restful import Api

from ..controllers.auth_controller import (
    RegisterResource,
    LoginResource,
    RefreshTokenResource,
    LogoutResource
)


def register_auth_routes(api: Api):
    """Register authentication related routes.

    Args:
        api: Flask-RESTful API instance
    """
    api.add_resource(RegisterResource, '/auth/register')
    api.add_resource(LoginResource, '/auth/login')
    api.add_resource(RefreshTokenResource, '/auth/refresh')
    api.add_resource(LogoutResource, '/auth/logout')