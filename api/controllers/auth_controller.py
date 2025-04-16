"""
Authentication controller for the API.

This module provides controller classes for handling authentication-related
requests, including registration, login, token refresh, and logout.
"""
from flask import request, current_app, g
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt,
    create_access_token
)

from . import BaseController
from ..schemas.auth import (
    register_schema,
    login_schema,
    refresh_token_schema,
    token_schema,
    user_schema
)
from ..middlewares.auth import generate_tokens
from services.auth.auth_service import AuthService
from database.repositories.user_repository import UserRepository


class RegisterResource(BaseController):
    """Resource for user registration."""

    def __init__(self):
        """Initialize the register resource."""
        self.auth_service = AuthService()
        self.user_repository = UserRepository()

    def post(self):
        """Handle user registration.

        Returns:
            tuple: Response data and status code
        """
        data = self._validate_schema(register_schema, request.json)

        # Check if user already exists
        if self.user_repository.get_by_email(data['email']):
            return self._error_response(
                "User with this email already exists",
                status_code=409
            )

        # Create the user
        user = self.auth_service.register_user(
            email=data['email'],
            password=data['password'],
            name=data['name']
        )

        # Generate tokens
        tokens = generate_tokens(user)

        # Return user data and tokens
        response_data = {
            'user': user_schema.dump(user),
            'tokens': token_schema.dump(tokens)
        }

        return self._success_response(
            data=response_data,
            message="User registered successfully",
            status_code=201
        )


class LoginResource(BaseController):
    """Resource for user login."""

    def __init__(self):
        """Initialize the login resource."""
        self.auth_service = AuthService()

    def post(self):
        """Handle user login.

        Returns:
            tuple: Response data and status code
        """
        data = self._validate_schema(login_schema, request.json)

        # Authenticate the user
        user = self.auth_service.authenticate_user(
            email=data['email'],
            password=data['password']
        )

        if not user:
            return self._error_response(
                "Invalid email or password",
                status_code=401
            )

        # Generate tokens
        tokens = generate_tokens(user)

        # Return user data and tokens
        response_data = {
            'user': user_schema.dump(user),
            'tokens': token_schema.dump(tokens)
        }

        return self._success_response(
            data=response_data,
            message="Login successful"
        )


class RefreshTokenResource(BaseController):
    """Resource for refreshing access tokens."""

    def post(self):
        """Handle token refresh.

        Returns:
            tuple: Response data and status code
        """
        data = self._validate_schema(refresh_token_schema, request.json)

        try:
            # Validate the refresh token
            user_id = self.auth_service.validate_refresh_token(data['refresh_token'])

            if not user_id:
                return self._error_response(
                    "Invalid refresh token",
                    status_code=401
                )

            # Get the user
            user = self.user_repository.get_by_id(user_id)

            if not user:
                return self._error_response(
                    "User not found",
                    status_code=404
                )

            # Generate new tokens
            tokens = generate_tokens(user)

            return self._success_response(
                data=token_schema.dump(tokens),
                message="Token refreshed successfully"
            )

        except Exception as e:
            current_app.logger.error(f"Token refresh error: {str(e)}")
            return self._error_response(
                "Invalid refresh token",
                status_code=401
            )


class LogoutResource(BaseController):
    """Resource for user logout."""

    @jwt_required()
    def post(self):
        """Handle user logout.

        Returns:
            tuple: Response data and status code
        """
        jti = get_jwt()["jti"]
        user_id = get_jwt_identity()

        # Add the token to the blocklist
        current_app.redis.set(
            f"revoked_token:{jti}",
            user_id,
            ex=current_app.config['JWT_ACCESS_TOKEN_EXPIRES_SECONDS']
        )

        return self._success_response(
            message="Successfully logged out"
        )