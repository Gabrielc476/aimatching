"""
Tests for authentication API routes.
"""

import pytest
import json
import jwt
from datetime import datetime


def test_register_success(client):
    """Test successful user registration."""
    # Prepare registration data
    registration_data = {
        'email': 'integration_test@example.com',
        'password': 'SecurePassword123!',
        'name': 'Integration Test User'
    }

    # Send registration request
    response = client.post(
        '/api/auth/register',
        data=json.dumps(registration_data),
        content_type='application/json'
    )

    # Check response
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'user' in data
    assert data['user']['email'] == 'integration_test@example.com'
    assert data['user']['name'] == 'Integration Test User'
    assert 'password_hash' not in data['user']
    assert 'id' in data['user']


def test_register_duplicate_email(client, test_user):
    """Test registration with an existing email."""
    # Prepare registration data with existing email
    registration_data = {
        'email': test_user.email,  # Use existing email
        'password': 'SecurePassword123!',
        'name': 'Duplicate Email User'
    }

    # Send registration request
    response = client.post(
        '/api/auth/register',
        data=json.dumps(registration_data),
        content_type='application/json'
    )

    # Check response
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'email already exists' in data['error'].lower()


def test_register_invalid_data(client):
    """Test registration with invalid data."""
    # Test with invalid email
    invalid_email_data = {
        'email': 'not-an-email',
        'password': 'SecurePassword123!',
        'name': 'Invalid Email User'
    }

    response = client.post(
        '/api/auth/register',
        data=json.dumps(invalid_email_data),
        content_type='application/json'
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'email' in data['error'].lower()

    # Test with weak password
    weak_password_data = {
        'email': 'valid@example.com',
        'password': 'weak',
        'name': 'Weak Password User'
    }

    response = client.post(
        '/api/auth/register',
        data=json.dumps(weak_password_data),
        content_type='application/json'
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'password' in data['error'].lower()

    # Test with missing fields
    missing_fields_data = {
        'email': 'valid@example.com'
        # Missing password and name
    }

    response = client.post(
        '/api/auth/register',
        data=json.dumps(missing_fields_data),
        content_type='application/json'
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_login_success(client, test_user, session):
    """Test successful login."""
    # Set a known password for the test user
    from utils.security import generate_password_hash
    known_password = 'TestPassword123!'
    test_user.password_hash = generate_password_hash(known_password)
    session.commit()

    # Prepare login data
    login_data = {
        'email': test_user.email,
        'password': known_password
    }

    # Send login request
    response = client.post(
        '/api/auth/login',
        data=json.dumps(login_data),
        content_type='application/json'
    )

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'user' in data
    assert data['user']['id'] == test_user.id
    assert data['user']['email'] == test_user.email
    assert 'tokens' in data
    assert 'access_token' in data['tokens']
    assert 'refresh_token' in data['tokens']

    # Verify access token
    from services.auth.token_service import TokenService
    token_service = TokenService()
    payload = token_service.verify_access_token(data['tokens']['access_token'])
    assert payload is not None
    assert payload['sub'] == test_user.id


def test_login_invalid_credentials(client, test_user, session):
    """Test login with invalid credentials."""
    # Set a known password for the test user
    from utils.security import generate_password_hash
    known_password = 'TestPassword123!'
    test_user.password_hash = generate_password_hash(known_password)
    session.commit()

    # Test with wrong email
    wrong_email_data = {
        'email': 'wrong@example.com',
        'password': known_password
    }

    response = client.post(
        '/api/auth/login',
        data=json.dumps(wrong_email_data),
        content_type='application/json'
    )

    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data

    # Test with wrong password
    wrong_password_data = {
        'email': test_user.email,
        'password': 'WrongPassword123!'
    }

    response = client.post(
        '/api/auth/login',
        data=json.dumps(wrong_password_data),
        content_type='application/json'
    )

    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data


def test_refresh_token(client, test_user):
    """Test token refresh."""
    # Generate a refresh token for the test user
    from services.auth.token_service import TokenService
    token_service = TokenService()
    refresh_token = token_service.generate_refresh_token(test_user.id)

    # Prepare refresh data
    refresh_data = {
        'refresh_token': refresh_token
    }

    # Send refresh request
    response = client.post(
        '/api/auth/refresh',
        data=json.dumps(refresh_data),
        content_type='application/json'
    )

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'tokens' in data
    assert 'access_token' in data['tokens']
    assert 'refresh_token' in data['tokens']

    # Verify new access token
    payload = token_service.verify_access_token(data['tokens']['access_token'])
    assert payload is not None
    assert payload['sub'] == test_user.id


def test_refresh_invalid_token(client):
    """Test refresh with invalid token."""
    # Prepare refresh data with invalid token
    refresh_data = {
        'refresh_token': 'invalid.token.here'
    }

    # Send refresh request
    response = client.post(
        '/api/auth/refresh',
        data=json.dumps(refresh_data),
        content_type='application/json'
    )

    # Check response
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data


def test_protected_route(client, auth_headers):
    """Test accessing a protected route with valid authentication."""
    # Create a protected route for testing
    # This should be a real protected route in your application

    # Send request to protected route
    response = client.get(
        '/api/profile',
        headers=auth_headers
    )

    # Check response
    assert response.status_code == 200


def test_protected_route_unauthorized(client):
    """Test accessing a protected route without authentication."""
    # Send request to protected route without auth headers
    response = client.get('/api/profile')

    # Check response
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data


def test_logout(client, test_user):
    """Test user logout."""
    # Generate a refresh token for the test user
    from services.auth.token_service import TokenService
    token_service = TokenService()
    refresh_token = token_service.generate_refresh_token(test_user.id)

    # Prepare logout data
    logout_data = {
        'refresh_token': refresh_token
    }

    # Send logout request
    response = client.post(
        '/api/auth/logout',
        data=json.dumps(logout_data),
        content_type='application/json'
    )

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data

    # Try to use the refresh token after logout
    refresh_data = {
        'refresh_token': refresh_token
    }

    response = client.post(
        '/api/auth/refresh',
        data=json.dumps(refresh_data),
        content_type='application/json'
    )

    # Check that token is no longer valid
    assert response.status_code == 401