"""
Development configuration for LinkedIn Job Matcher.
"""

import os
from .base import BaseConfig


class DevelopmentConfig(BaseConfig):
    """Development environment specific configuration."""

    DEBUG = True

    # Enable more detailed SQL logging
    SQLALCHEMY_ECHO = True

    # Development-specific settings
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']

    # Less secure but easier for development
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24  # 24 hours

    # Email testing - use mailtrap or other testing service
    MAIL_SERVER = os.getenv('DEV_MAIL_SERVER', 'smtp.mailtrap.io')
    MAIL_PORT = int(os.getenv('DEV_MAIL_PORT', 2525))
    MAIL_USERNAME = os.getenv('DEV_MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('DEV_MAIL_PASSWORD', '')

    # More lenient rate limiting for development
    RATELIMIT_DEFAULT = "1000 per day, 500 per hour"

    # Shorter wait time between scraping requests for faster development
    SCRAPE_PAGE_WAIT_MIN = 1
    SCRAPE_PAGE_WAIT_MAX = 2

    # Enable Celery task eager execution for easier debugging
    CELERY_TASK_ALWAYS_EAGER = os.getenv('CELERY_TASK_ALWAYS_EAGER', 'false').lower() == 'true'

    # Development logging - more verbose
    LOG_LEVEL = 'DEBUG'

    # Development database - use SQLite by default for simplicity
    DATABASE_URI = os.getenv('DEV_DATABASE_URI', 'sqlite:///dev.db')

    # Disable real scraping for development by default
    USE_MOCK_SCRAPER = os.getenv('USE_MOCK_SCRAPER', 'true').lower() == 'true'

    # Mock data settings
    MOCK_DATA_DIR = os.path.join(os.getcwd(), 'tests', 'fixtures')

    # Enable CSRF protection but with less strict requirements
    WTF_CSRF_ENABLED = True
    WTF_CSRF_CHECK_DEFAULT = False  # Don't check by default in development

    # Enable debug toolbar for development
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # Development-specific upload folder
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'dev_uploads')