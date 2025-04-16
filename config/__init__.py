"""
Configuration package for LinkedIn Job Matcher.
This module handles configuration loading and environment-specific settings.
"""

import os
from typing import Any

from .development import DevelopmentConfig
from .production import ProductionConfig
from .testing import TestingConfig

# Map environment names to config classes
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}


def get_config() -> Any:
    """
    Get the appropriate configuration based on the environment.

    Returns:
        Config object for the current environment
    """
    env = os.getenv('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)