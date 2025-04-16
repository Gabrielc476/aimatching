"""
Error handling middleware for the API.

This module provides middleware functions for handling and formatting
API errors in a consistent way.
"""
import traceback
from marshmallow import ValidationError
from flask import Blueprint, jsonify, current_app
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError


class APIError(Exception):
    """Custom API error class.

    Attributes:
        message: Error message
        status_code: HTTP status code
        payload: Additional error payload
    """

    def __init__(self, message, status_code=400, payload=None):
        """Initialize the API error.

        Args:
            message: Error message
            status_code: HTTP status code
            payload: Additional error payload
        """
        super().__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Convert the error to a dictionary.

        Returns:
            dict: Error dictionary
        """
        error_dict = {
            'status': 'error',
            'message': self.message
        }
        if self.payload:
            error_dict['payload'] = self.payload
        return error_dict


def register_error_handlers(blueprint: Blueprint):
    """Register error handlers for the API blueprint.

    Args:
        blueprint: Flask blueprint
    """

    @blueprint.errorhandler(APIError)
    def handle_api_error(error):
        """Handle custom API errors."""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @blueprint.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle Marshmallow validation errors."""
        return jsonify({
            'status': 'error',
            'message': 'Validation error',
            'errors': error.messages
        }), 400

    @blueprint.errorhandler(HTTPException)
    def handle_http_error(error):
        """Handle Werkzeug HTTP exceptions."""
        response = jsonify({
            'status': 'error',
            'message': error.description,
            'code': error.code
        })
        response.status_code = error.code
        return response

    @blueprint.errorhandler(SQLAlchemyError)
    def handle_db_error(error):
        """Handle SQLAlchemy database errors."""
        # Log the error for debugging
        current_app.logger.error(f"Database error: {str(error)}")
        current_app.logger.error(traceback.format_exc())

        return jsonify({
            'status': 'error',
            'message': 'Database error occurred'
        }), 500

    @blueprint.errorhandler(Exception)
    def handle_generic_error(error):
        """Handle any unhandled exceptions."""
        # Log the error for debugging
        current_app.logger.error(f"Unhandled exception: {str(error)}")
        current_app.logger.error(traceback.format_exc())

        # In development, we might want to show more details
        if current_app.config.get('DEBUG', False):
            return jsonify({
                'status': 'error',
                'message': str(error),
                'traceback': traceback.format_exc()
            }), 500

        # In production, show a generic message
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred'
        }), 500