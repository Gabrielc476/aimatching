"""
Rate limiting middleware for the API.

This module provides middleware functions for rate limiting API requests
to prevent abuse and ensure fair usage of the API.
"""
from flask import Flask, request, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = None


def get_user_id():
    """Get the user ID from the current request context.

    Used as a key function for rate limiting based on user ID.

    Returns:
        int or str: User ID if authenticated, IP address otherwise
    """
    if hasattr(g, 'current_user') and g.current_user:
        return str(g.current_user.id)
    return get_remote_address()


def init_rate_limiter(app: Flask):
    """Initialize the rate limiter middleware.

    Args:
        app: Flask application instance
    """
    global limiter

    limiter = Limiter(
        app=app,
        key_func=get_user_id,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=app.config['REDIS_URL'],
        strategy="fixed-window-elastic-expiry"
    )

    # Define rate limits for specific endpoints
    limiter.limit("5 per minute")(app.view_functions['api.auth_login'])
    limiter.limit("3 per minute")(app.view_functions['api.auth_register'])
    limiter.limit("3 per minute")(app.view_functions['api.auth_refresh'])

    # Higher limits for authenticated users for certain endpoints
    limiter.limit("300 per day")(app.view_functions['api.jobs_list'])
    limiter.limit("100 per hour")(app.view_functions['api.jobs_search'])
    limiter.limit("50 per hour")(app.view_functions['api.match_analyze'])


def limit_by_key(rate_string, key_func):
    """Create a decorator to apply rate limits based on a custom key.

    Args:
        rate_string: Rate limit string (e.g. "5 per minute")
        key_func: Function to extract the rate limit key

    Returns:
        Decorator function to apply the rate limit
    """

    def decorator(f):
        return limiter.limit(rate_string, key_func=key_func)(f)

    return decorator