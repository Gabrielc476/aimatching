"""
Tests for AuthService.
"""

import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from services.auth.auth_service import AuthService
from services.auth.token_service import TokenService
from utils.security import generate_password_hash, verify_password
from models.user import User


def test_register_user_success(session):
    """Test successful user registration."""
    # Initialize services
    auth_service = AuthService(session)

    # Register a new user
    user_data = {
        'email': 'newuser@example.com',
        'password': 'StrongPass123!',
        'name': 'New User'
    }

    user, error = auth_service.register_user(user_data)

    # Verify registration was successful
    assert user is not None
    assert error is None
    assert user.email == 'newuser@example.com'
    assert user.name == 'New User'
    assert verify_password('StrongPass123!', user.password_hash)

    # Verify user exists in database
    db_user = session.query(User).filter_by(email='newuser@example.com').first()
    assert db_user is not None
    assert db_user.id == user.id


def test_register_user_existing_email(session, test_user):
    """Test registration with an existing email."""
    # Initialize services
    auth_service = AuthService(session)

    # Try to register with an existing email
    user_data = {
        'email': test_user.email,  # Existing email
        'password': 'StrongPass123!',
        'name': 'Duplicate User'
    }

    user, error = auth_service.register_user(user_data)

    # Verify registration failed
    assert user is None
    assert error is not None
    assert 'email already exists' in error.lower()


def test_register_user_invalid_data(session):
    """Test registration with invalid data."""
    # Initialize services
    auth_service = AuthService(session)

    # Try to register with invalid email
    invalid_email_data = {
        'email': 'invalid-email',
        'password': 'StrongPass123!',
        'name': 'Invalid Email User'
    }

    user, error = auth_service.register_user(invalid_email_data)

    # Verify registration failed
    assert user is None
    assert error is not None
    assert 'email' in error.lower()

    # Try to register with weak password
    weak_password_data = {
        'email': 'valid@example.com',
        'password': 'weak',
        'name': 'Weak Password User'
    }

    user, error = auth_service.register_user(weak_password_data)

    # Verify registration failed
    assert user is None
    assert error is not None
    assert 'password' in error.lower()

    # Try to register without name
    no_name_data = {
        'email': 'valid@example.com',
        'password': 'StrongPass123!'
        # No name
    }

    user, error = auth_service.register_user(no_name_data)

    # Verify registration failed
    assert user is None
    assert error is not None
    assert 'name' in error.lower()


def test_login_user_success(session, test_user):
    """Test successful user login."""
    # Initialize services
    auth_service = AuthService(session)

    # Set a known password for the test user
    known_password = 'TestPassword123!'
    test_user.password_hash = generate_password_hash(known_password)
    session.commit()

    # Login with correct credentials
    user, tokens, error = auth_service.login_user(test_user.email, known_password)

    # Verify login was successful
    assert user is not None
    assert tokens is not None
    assert error is None
    assert user.id == test_user.id
    assert 'access_token' in tokens
    assert 'refresh_token' in tokens

    # Verify tokens are valid
    token_service = TokenService()
    access_payload = token_service.verify_access_token(tokens['access_token'])
    assert access_payload is not None
    assert access_payload['sub'] == test_user.id

    refresh_payload = token_service.verify_refresh_token(tokens['refresh_token'])
    assert refresh_payload is not None
    assert refresh_payload['sub'] == test_user.id


def test_login_user_invalid_credentials(session, test_user):
    """Test login with invalid credentials."""
    # Initialize services
    auth_service = AuthService(session)

    # Set a known password for the test user
    known_password = 'TestPassword123!'
    test_user.password_hash = generate_password_hash(known_password)
    session.commit()

    # Login with incorrect email
    user, tokens, error = auth_service.login_user('wrong@example.com', known_password)

    # Verify login failed
    assert user is None
    assert tokens is None
    assert error is not None
    assert 'invalid email or password' in error.lower()

    # Login with incorrect password
    user, tokens, error = auth_service.login_user(test_user.email, 'WrongPassword123!')

    # Verify login failed
    assert user is None
    assert tokens is None
    assert error is not None
    assert 'invalid email or password' in error.lower()


def test_refresh_token_success(session, test_user):
    """Test successful token refresh."""
    # Initialize services
    auth_service = AuthService(session)
    token_service = TokenService()

    # Generate a refresh token for the test user
    refresh_token = token_service.generate_refresh_token(test_user.id)

    # Refresh the token
    new_tokens, error = auth_service.refresh_token(refresh_token)

    # Verify token refresh was successful
    assert new_tokens is not None
    assert error is None
    assert 'access_token' in new_tokens
    assert 'refresh_token' in new_tokens

    # Verify new tokens are valid
    access_payload = token_service.verify_access_token(new_tokens['access_token'])
    assert access_payload is not None
    assert access_payload['sub'] == test_user.id

    refresh_payload = token_service.verify_refresh_token(new_tokens['refresh_token'])
    assert refresh_payload is not None
    assert refresh_payload['sub'] == test_user.id


def test_refresh_token_invalid(session):
    """Test token refresh with invalid token."""
    # Initialize services
    auth_service = AuthService(session)

    # Try to refresh with invalid token
    new_tokens, error = auth_service.refresh_token('invalid.token.here')

    # Verify token refresh failed
    assert new_tokens is None
    assert error is not None
    assert 'invalid or expired token' in error.lower()


@patch('services.auth.token_service.jwt.decode')
def test_refresh_token_expired(mock_jwt_decode, session, test_user):
    """Test token refresh with expired token."""
    # Mock jwt.decode to raise an ExpiredSignatureError
    mock_jwt_decode.side_effect = jwt.ExpiredSignatureError("Token expired")

    # Initialize services
    auth_service = AuthService(session)
    token_service = TokenService()

    # Generate a refresh token for the test user
    refresh_token = token_service.generate_refresh_token(test_user.id)

    # Try to refresh the token
    new_tokens, error = auth_service.refresh_token(refresh_token)

    # Verify token refresh failed
    assert new_tokens is None
    assert error is not None
    assert 'token expired' in error.lower()


def test_logout_user(session, test_user):
    """Test user logout."""
    # Initialize services
    auth_service = AuthService(session)
    token_service = TokenService()

    # Generate tokens for the test user
    refresh_token = token_service.generate_refresh_token(test_user.id)

    # Logout the user
    success = auth_service.logout_user(refresh_token)

    # Verify logout was successful
    assert success is True

    # Try to refresh the token after logout (should fail)
    new_tokens, error = auth_service.refresh_token(refresh_token)
    assert new_tokens is None
    assert error is not None