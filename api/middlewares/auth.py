"""
Authentication middleware for the API.

This module provides middleware functions for JWT-based authentication.
"""
import datetime
from functools import wraps

from flask import Flask, request, g, current_app
from flask_jwt_extended import (
    JWTManager,
    verify_jwt_in_request,
    get_jwt_identity,
    create_access_token,
    create_refresh_token
)

from models import User
from database.repositories import user_repository


def init_auth_middleware(app: Flask):
    """Initialize the JWT authentication middleware.

    Args:
        app: Flask application instance
    """
    jwt = JWTManager(app)

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        """Convert user object to a JWT identity."""
        if isinstance(user, dict):
            return user.get('id')
        return user.id if hasattr(user, 'id') else user

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """Load user from the database based on JWT identity."""
        identity = jwt_data["sub"]
        return user_repository.get_by_id(identity)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """Check if a token has been revoked."""
        jti = jwt_payload["jti"]
        token = app.redis.get(f"revoked_token:{jti}")
        return token is not None

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired token errors."""
        return {
            'status': 'error',
            'message': 'The token has expired',
            'error': 'token_expired'
        }, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Handle invalid token errors."""
        return {
            'status': 'error',
            'message': 'Signature verification failed',
            'error': 'invalid_token'
        }, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Handle missing token errors."""
        return {
            'status': 'error',
            'message': 'Request does not contain an access token',
            'error': 'authorization_required'
        }, 401


def jwt_required(fn):
    """Decorator that requires a valid JWT token to be present in the request.

    Args:
        fn: The function to decorate

    Returns:
        The decorated function
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()

        # Load the user and make it available in the request context
        g.current_user = user_repository.get_by_id(user_id)
        if not g.current_user:
            return {
                'status': 'error',
                'message': 'User not found',
                'error': 'user_not_found'
            }, 401

        return fn(*args, **kwargs)

    return wrapper


def generate_tokens(user):
    """Generate access and refresh tokens for a user.

    Args:
        user: User object or user ID

    Returns:
        dict: Dictionary containing the tokens and related information
    """
    access_token_expires = datetime.timedelta(
        minutes=current_app.config['JWT_ACCESS_TOKEN_EXPIRES_MINUTES']
    )
    refresh_token_expires = datetime.timedelta(
        days=current_app.config['JWT_REFRESH_TOKEN_EXPIRES_DAYS']
    )

    access_token = create_access_token(
        identity=user,
        expires_delta=access_token_expires
    )

    refresh_token = create_refresh_token(
        identity=user,
        expires_delta=refresh_token_expires
    )

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': access_token_expires.total_seconds()
    }