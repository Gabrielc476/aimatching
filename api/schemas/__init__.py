"""
Schemas module for the API.

This module provides schemas for request validation and response serialization.
"""
from flask_marshmallow import Marshmallow

ma = Marshmallow()


def init_marshmallow(app):
    """Initialize Marshmallow with the Flask application.

    Args:
        app: Flask application instance
    """
    ma.init_app(app)