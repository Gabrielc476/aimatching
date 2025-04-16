"""
Middlewares module for the API.

This module provides middleware functions for request processing,
authentication, rate limiting, and error handling.
"""
from flask import Flask

from .auth import init_auth_middleware
from .rate_limit import init_rate_limiter


def init_middlewares(app: Flask):
    """Initialize all middlewares for the application.

    Args:
        app: Flask application instance
    """
    # Initialize authentication middleware
    init_auth_middleware(app)

    # Initialize rate limiting middleware
    init_rate_limiter(app)