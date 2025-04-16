"""
Configurações da aplicação
Configurações para diferentes ambientes (desenvolvimento, produção, teste).
"""
import os
from datetime import timedelta


class Config:
    """Configuração base."""
    VERSION = "1.0.0"
    SECRET_KEY = os.getenv("SECRET_KEY", "linkedin-job-matcher-secret-key")
    DEBUG = False
    TESTING = False

    # JWT Settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI",
        "postgresql://postgres:postgres@localhost:5432/linkedin_job_matcher"
    )

    @classmethod
    def get_db_uri_with_encoding(cls):
        """Get database URI with proper encoding parameters."""
        base_uri = cls.SQLALCHEMY_DATABASE_URI

        # Add encoding parameters if not already present
        if "?" not in base_uri:
            return f"{base_uri}?client_encoding=utf8"
        elif "client_encoding=" not in base_uri:
            return f"{base_uri}&client_encoding=utf8"
        return base_uri

    # Redis settings
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Cache settings
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos

    # CORS settings
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # Claude API settings
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-7-sonnet-20250219")

    # Upload settings
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "txt"}

    # WebSocket settings
    SOCKET_IO_PING_TIMEOUT = 60
    SOCKET_IO_PING_INTERVAL = 25

    # Celery settings
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    # LinkedIn Scraping settings
    LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME", "")
    LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")
    SCRAPING_INTERVAL = 3600  # 1 hour


class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento."""
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Configuração para ambiente de teste."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(Config):
    """Configuração para ambiente de produção."""
    SECRET_KEY = os.getenv("SECRET_KEY", "production-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")

    # Cache settings for production
    CACHE_DEFAULT_TIMEOUT = 600  # 10 minutos

    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "200 per day;50 per hour;5 per minute"


# Mapeamento de ambientes para configurações
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}