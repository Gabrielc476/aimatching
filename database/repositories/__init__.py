"""
Repository package providing data access layer for the application.
"""

from .base_repository import BaseRepository
from .user_repository import UserRepository
from .profile_repository import ProfileRepository
from .resume_repository import ResumeRepository
from .job_repository import JobRepository
from .match_repository import MatchRepository

__all__ = [
    'BaseRepository',
    'UserRepository',
    'ProfileRepository',
    'ResumeRepository',
    'JobRepository',
    'MatchRepository'
]