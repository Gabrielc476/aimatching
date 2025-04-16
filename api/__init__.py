"""
API module for LinkedIn Job Matcher.

This package defines the RESTful API layer of the application, including routes,
controllers, schemas for validation, and middlewares.
"""
from flask import Blueprint
from flask_restful import Api

from .routes import register_routes


def create_api_blueprint(app):
    """Create and configure the API blueprint with all routes.

    Args:
        app: The Flask application instance

    Returns:
        Blueprint: The configured API blueprint
    """
    api_bp = Blueprint('api', __name__, url_prefix='/api')
    api = Api(api_bp)

    # Register all API routes
    register_routes(api)

    # Register error handlers
    from .middlewares.error_handler import register_error_handlers
    register_error_handlers(api_bp)

    return api_bp