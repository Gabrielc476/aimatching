"""
Base configuration for LinkedIn Job Matcher.
"""

import os
from datetime import timedelta


class BaseConfig:
    """Base configuration class with common settings."""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'top-secret-key-for-dev-only')
    DEBUG = False
    TESTING = False

    # API Configuration
    API_PREFIX = '/api'
    API_VERSION = 'v1'

    # Database
    DATABASE_URI = os.getenv('DATABASE_URI', 'postgresql://user:password@localhost:5432/linkedin_job_matcher')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # JWT Authentication
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Security
    BCRYPT_LOG_ROUNDS = 12

    # CORS
    CORS_ORIGINS = ['http://localhost:3000', 'https://linkedin-job-matcher.com']

    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_STRATEGY = 'fixed-window'

    # File Storage
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'odt', 'rtf'}

    # Claude API
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY', '')
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-7-sonnet-20250219')

    # LinkedIn Scraping
    LINKEDIN_USERNAME = os.getenv('LINKEDIN_USERNAME', '')
    LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD', '')

    # Proxies Configuration
    USE_PROXIES = os.getenv('USE_PROXIES', 'false').lower() == 'true'
    PROXY_API_KEY = os.getenv('PROXY_API_KEY', '')

    # Scraping Limits
    SCRAPE_PAGE_WAIT_MIN = 2  # Minimum wait time between pages in seconds
    SCRAPE_PAGE_WAIT_MAX = 5  # Maximum wait time between pages in seconds
    SCRAPE_REQUEST_TIMEOUT = 30  # Request timeout in seconds

    # Matching Configuration
    MIN_MATCH_SCORE = 50  # Minimum score to consider a match
    EXCELLENT_MATCH_THRESHOLD = 85  # Threshold for excellent matches
    GOOD_MATCH_THRESHOLD = 70  # Threshold for good matches

    # Email Notifications
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'notificacoes@linkedin-job-matcher.com')

    # Websocket Configuration
    WEBSOCKET_PING_INTERVAL = 25  # Ping interval in seconds
    WEBSOCKET_PING_TIMEOUT = 10  # Ping timeout in seconds
    WEBSOCKET_MAX_SIZE = 1024 * 1024  # Maximum message size

    # Celery Configuration
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_TIMEZONE = 'UTC'
    CELERY_TASK_ALWAYS_EAGER = False

    # Session Configuration
    SESSION_TYPE = 'redis'
    SESSION_REDIS = REDIS_URL
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'