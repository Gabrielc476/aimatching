"""
Controllers module for the API.

This module provides controller classes for handling API requests
and implementing business logic.
"""
from flask_restful import Resource
from flask import g, request, current_app
from marshmallow import ValidationError

from ..middlewares.error_handler import APIError


class BaseController(Resource):
    """Base controller class with common functionality.

    This class provides common functionality for all controllers, including
    request validation, response formatting, and error handling.
    """

    def _validate_schema(self, schema, data, partial=False):
        """Validate request data against a schema.

        Args:
            schema: Marshmallow schema to validate against
            data: Request data to validate
            partial: Whether to allow partial validation

        Returns:
            dict: Validated data

        Raises:
            ValidationError: If validation fails
        """
        try:
            return schema.load(data, partial=partial)
        except ValidationError as err:
            current_app.logger.warning(f"Validation error: {err.messages}")
            raise

    def _success_response(self, data=None, message=None, status_code=200):
        """Create a success response.

        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code

        Returns:
            tuple: Response data and status code
        """
        response = {'status': 'success'}

        if data is not None:
            response['data'] = data

        if message is not None:
            response['message'] = message

        return response, status_code

    def _error_response(self, message, status_code=400, payload=None):
        """Create an error response.

        Args:
            message: Error message
            status_code: HTTP status code
            payload: Additional error payload

        Returns:
            tuple: Error response and status code
        """
        response = {'status': 'error', 'message': message}

        if payload is not None:
            response['payload'] = payload

        return response, status_code

    def _get_current_user(self):
        """Get the current authenticated user.

        Returns:
            User: Current user object

        Raises:
            APIError: If no user is authenticated
        """
        if not hasattr(g, 'current_user') or not g.current_user:
            raise APIError("Authentication required", status_code=401)
        return g.current_user

    def _get_pagination_params(self):
        """Extract pagination parameters from the request.

        Returns:
            tuple: (page, per_page) pagination parameters
        """
        try:
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 20)), 100)
            return max(page, 1), max(per_page, 1)
        except ValueError:
            return 1, 20