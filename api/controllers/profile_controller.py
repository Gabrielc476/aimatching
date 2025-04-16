"""
Profile controller for the API.

This module provides controller classes for handling profile-related
requests, including retrieving and updating user profiles.
"""
from flask import request, current_app
from flask_jwt_extended import jwt_required

from . import BaseController
from ..middlewares.auth import jwt_required
from ..schemas.profiles import profile_schema, profile_update_schema
from database.repositories.profile_repository import ProfileRepository


class ProfileResource(BaseController):
    """Resource for user profile operations."""

    def __init__(self):
        """Initialize the profile resource."""
        self.profile_repository = ProfileRepository()

    @jwt_required
    def get(self):
        """Get the current user's profile.

        Returns:
            tuple: Response data and status code
        """
        user = self._get_current_user()

        # Get the user's profile
        profile = self.profile_repository.get_by_user_id(user.id)

        if not profile:
            return self._error_response(
                "Profile not found",
                status_code=404
            )

        return self._success_response(data=profile_schema.dump(profile))

    @jwt_required
    def put(self):
        """Update the current user's profile.

        Returns:
            tuple: Response data and status code
        """
        user = self._get_current_user()
        data = self._validate_schema(profile_update_schema, request.json)

        # Get the user's profile
        profile = self.profile_repository.get_by_user_id(user.id)

        if not profile:
            # Create a new profile if it doesn't exist
            profile = self.profile_repository.create(user_id=user.id, **data)
            status_code = 201
            message = "Profile created successfully"
        else:
            # Update the existing profile
            profile = self.profile_repository.update(profile.id, **data)
            status_code = 200
            message = "Profile updated successfully"

        # If profile was updated, trigger matching job update
        if status_code == 200:
            from tasks.matching_tasks import update_user_matches
            update_user_matches.delay(user.id)

        return self._success_response(
            data=profile_schema.dump(profile),
            message=message,
            status_code=status_code
        )