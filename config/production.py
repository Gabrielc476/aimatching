"""
Production configuration for LinkedIn Job Matcher.
"""

import os
from .base import BaseConfig


class ProductionConfig(BaseConfig):
    """Production environment specific configuration."""

    # Ensure debug is disabled in production
    DEBUG = False

    # Require HTTPS for cookies
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

    # Stricter Content Security Policy
    CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'script-src': "'self'",
        'style-src': "'self' https://fonts.googleapis.com",
        'font-src': "'self' https://fonts.gstatic.com",
        'img-src': "'self' data:",
        'connect-src': "'self'"
    }

    # Production database - must be set in environment
    DATABASE_URI = os.getenv('DATABASE_URI')
    if not DATABASE_URI:
        raise ValueError("Production DATABASE_URI must be set in environment variables")

    # Redis configuration - must be set in environment
    REDIS_URL = os.getenv('REDIS_URL')
    if not REDIS_URL:
        raise ValueError("Production REDIS_URL must be set in environment variables")

    # Secret keys - must be set in environment
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("Production SECRET_KEY must be set in environment variables")

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        raise ValueError("Production JWT_SECRET_KEY must be set in environment variables")

    # Claude API key - must be set in environment
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    if not CLAUDE_API_KEY:
        raise ValueError("Production CLAUDE_API_KEY must be set in environment variables")

    # LinkedIn credentials - must be set in environment
    LINKEDIN_USERNAME = os.getenv('LINKEDIN_USERNAME')
    LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')
    if not LINKEDIN_USERNAME or not LINKEDIN_PASSWORD:
        raise ValueError("Production LinkedIn credentials must be set in environment variables")

    # CORS settings - restrict to actual domains
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')

    # Rate limiting - more strict for production
    RATELIMIT_DEFAULT = "100 per day, 20 per hour"

    # Longer wait times between scraping requests to avoid detection
    SCRAPE_PAGE_WAIT_MIN = 3
    SCRAPE_PAGE_WAIT_MAX = 8

    # Production should use real proxies
    USE_PROXIES = True
    PROXY_API_KEY = os.getenv('PROXY_API_KEY')

    # Enable strict CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_CHECK_DEFAULT = True

    # Production-appropriate log level
    LOG_LEVEL = 'INFO'

    # Disable debug toolbar
    DEBUG_TB_ENABLED = False

    # AWS S3 configuration for file storage
    USE_S3 = os.getenv('USE_S3', 'true').lower() == 'true'
    S3_BUCKET = os.getenv('S3_BUCKET')
    S3_REGION = os.getenv('S3_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

    # Sentry error tracking
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    USE_SENTRY = os.getenv('USE_SENTRY', 'true').lower() == 'true'

    # Email configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = True

    # Security headers
    SECURE_HEADERS = {
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'X-Content-Type-Options': 'nosniff',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }