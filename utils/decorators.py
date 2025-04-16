"""
Decorator utilities for LinkedIn Job Matcher.
"""

import time
import functools
import logging
from typing import Callable, Any, Dict, Optional
from flask import request, jsonify, g, current_app
import redis
from functools import wraps
from ..tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def require_auth(f: Callable) -> Callable:
    """
    Decorator to require authentication for a route.

    This decorator checks for a valid JWT token in the request header and
    adds the authenticated user ID to Flask's g object.

    Args:
        f: Function to decorate

    Returns:
        Decorated function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        from ..services.auth.token_service import TokenService

        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401

        try:
            # Assuming format: "Bearer <token>"
            token_parts = auth_header.split()

            if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
                return jsonify({'error': 'Unauthorized', 'message': 'Invalid token format'}), 401

            token = token_parts[1]
            token_service = TokenService()
            payload = token_service.verify_access_token(token)

            if not payload:
                return jsonify({'error': 'Unauthorized', 'message': 'Invalid or expired token'}), 401

            # Store user ID in Flask's g object for use in the route
            g.user_id = payload.get('sub')

            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return jsonify({'error': 'Unauthorized', 'message': 'Authentication failed'}), 401

    return decorated_function


def rate_limit(limit: int = 60, per: int = 60, key_func: Optional[Callable] = None) -> Callable:
    """
    Decorator to apply rate limiting to a route.

    Args:
        limit: Maximum number of requests allowed
        per: Time period in seconds
        key_func: Optional function to derive the rate limit key (defaults to IP address)

    Returns:
        Decorator function
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get Redis client from app config
            redis_client = current_app.extensions.get('redis', None)

            if not redis_client:
                # Fall back to direct connection if not available in app extensions
                redis_url = current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
                redis_client = redis.from_url(redis_url)

            # Determine the rate limit key
            if key_func:
                key = key_func()
            else:
                # Default to IP address
                key = request.remote_addr or 'unknown'

            # Create a Redis key for this route and requester
            redis_key = f"rate_limit:{request.path}:{key}"

            # Get current count
            current = redis_client.get(redis_key)
            current = int(current) if current else 0

            # Check if rate limit exceeded
            if current >= limit:
                return jsonify({
                    'error': 'Too Many Requests',
                    'message': f'Rate limit of {limit} requests per {per} seconds exceeded'
                }), 429

            # Increment the counter
            pipe = redis_client.pipeline()
            pipe.incr(redis_key)
            # Set the expiration if this is the first request
            if current == 0:
                pipe.expire(redis_key, per)
            pipe.execute()

            # Execute the route function
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def async_task(f: Callable) -> Callable:
    """
    Decorator to execute a function asynchronously using Celery.

    Args:
        f: Function to execute asynchronously

    Returns:
        Decorated function that returns a task object
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Create a Celery task dynamically
        task = celery_app.task(f)
        # Execute the task asynchronously
        return task.delay(*args, **kwargs)

    return decorated_function


def timed(f: Callable) -> Callable:
    """
    Decorator to measure and log the execution time of a function.

    Args:
        f: Function to measure

    Returns:
        Decorated function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        elapsed_time = time.time() - start_time

        # Log execution time
        logger.info(f"Function {f.__name__} executed in {elapsed_time:.4f} seconds")

        return result

    return decorated_function


def cache(ttl: int = 300, key_prefix: str = "cache") -> Callable:
    """
    Decorator to cache function results in Redis.

    Args:
        ttl: Time-to-live for cache entries in seconds
        key_prefix: Prefix for Redis keys

    Returns:
        Decorator function
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            import json
            import hashlib

            # Get Redis client from app config
            redis_client = current_app.extensions.get('redis', None)

            if not redis_client:
                # Fall back to direct connection if not available in app extensions
                redis_url = current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
                redis_client = redis.from_url(redis_url)

            # Create a cache key based on function name, args, and kwargs
            key_parts = [f.__name__]

            # Add args to key
            for arg in args:
                key_parts.append(str(arg))

            # Add kwargs to key (sorted for consistency)
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={v}")

            # Create a hash of the key parts for a shorter key
            key_str = ":".join(key_parts)
            hashed_key = hashlib.md5(key_str.encode('utf-8')).hexdigest()
            cache_key = f"{key_prefix}:{hashed_key}"

            # Try to get from cache
            cached = redis_client.get(cache_key)

            if cached:
                return json.loads(cached)

            # Execute the function
            result = f(*args, **kwargs)

            # Cache the result
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result, default=str)  # Use default=str for non-serializable objects
            )

            return result

        return decorated_function

    return decorator


def retry(max_retries: int = 3, delay: int = 1, backoff: int = 2, exceptions: tuple = (Exception,)) -> Callable:
    """
    Decorator to retry a function on failure.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for retry delay
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorator function
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            mtries, mdelay = max_retries, delay
            while mtries > 0:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    logger.warning(f"Retry: {f.__name__} failed with {e.__class__.__name__}: {str(e)}")
                    mtries -= 1
                    if mtries == 0:
                        raise

                    logger.info(f"Retrying in {mdelay} seconds...")
                    time.sleep(mdelay)
                    mdelay *= backoff

            return f(*args, **kwargs)

        return decorated_function

    return decorator