"""
Testing configuration for LinkedIn Job Matcher.
"""

import os
import tempfile
from .base import BaseConfig


class TestingConfig(BaseConfig):
    """Testing environment specific configuration."""

    # Enable testing mode
    TESTING = True
    DEBUG = False

    # Use SQLite in-memory database for testing
    DATABASE_URI = os.getenv('TEST_DATABASE_URI', 'sqlite:///:memory:')

    # Disable CSRF protection for testing
    WTF_CSRF_ENABLED = False

    # Use eager task execution for testing
    CELERY_TASK_ALWAYS_EAGER = True

    # Use a temporary folder for uploads
    UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'test_uploads')

    # Use test-specific Redis database
    REDIS_URL = os.getenv('TEST_REDIS_URL', 'redis://localhost:6379/9')

    # Mock external services
    USE_MOCK_SCRAPER = True
    USE_MOCK_CLAUDE = True

    # Email testing
    MAIL_SUPPRESS_SEND = True

    # JWT shortened expiration for testing
    JWT_ACCESS_TOKEN_EXPIRES = 300  # 5 minutes
    JWT_REFRESH_TOKEN_EXPIRES = 600  # 10 minutes

    # Test-specific settings
    PRESERVE_CONTEXT_ON_EXCEPTION = False

    # Testing credentials
    LINKEDIN_USERNAME = 'test_user'
    LINKEDIN_PASSWORD = 'test_password'
    CLAUDE_API_KEY = 'test_api_key'

    # Enable very lenient rate limiting for tests
    RATELIMIT_ENABLED = False

    # Disable authentication for certain test routes
    BYPASS_AUTH_FOR_TESTING = True

    # Testing fixtures
    TEST_DATA_DIR = os.path.join(os.getcwd(), 'tests', 'fixtures')

    # Deterministic scrape waits for testing
    SCRAPE_PAGE_WAIT_MIN = 0.01
    SCRAPE_PAGE_WAIT_MAX = 0.01

    # Disable S3 in testing mode
    USE_S3 = False

    # Test-specific log level
    LOG_LEVEL = 'ERROR'  # Only log errors during tests

    @classmethod
    def init_app(cls, app):
        """Initialize testing-specific app settings."""
        # Create upload folder if it doesn't exist
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)

        # Register clean up function to remove test files
        import atexit
        import shutil

        def cleanup_test_files():
            if os.path.exists(cls.UPLOAD_FOLDER):
                shutil.rmtree(cls.UPLOAD_FOLDER)

        atexit.register(cleanup_test_files)