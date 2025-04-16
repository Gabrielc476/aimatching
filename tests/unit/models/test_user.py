"""
Tests for User model.
"""

import pytest
from datetime import datetime
from models.user import User


def test_user_creation(session):
    """Test User model creation."""
    # Create user
    user = User(
        email='test_create@example.com',
        password_hash='hashed_password',
        name='Test User Creation',
        created_at=datetime.utcnow()
    )

    session.add(user)
    session.commit()

    # Query user
    retrieved_user = session.query(User).filter_by(email='test_create@example.com').first()

    # Assert user was created correctly
    assert retrieved_user is not None
    assert retrieved_user.email == 'test_create@example.com'
    assert retrieved_user.password_hash == 'hashed_password'
    assert retrieved_user.name == 'Test User Creation'
    assert retrieved_user.created_at is not None
    assert retrieved_user.id is not None


def test_user_relationships(session, test_user, test_profile, test_resume):
    """Test User relationships with Profile and Resume."""
    # Refresh the user from the database
    user = session.query(User).get(test_user.id)

    # Test profile relationship
    assert user.profile is not None
    assert user.profile.user_id == user.id
    assert user.profile.title == 'Software Engineer'

    # Test resumes relationship
    assert len(user.resumes) > 0
    assert user.resumes[0].user_id == user.id
    assert user.resumes[0].filename == 'test_resume.pdf'


def test_user_unique_email_constraint(session):
    """Test that users must have unique email addresses."""
    # Create first user
    user1 = User(
        email='unique_test@example.com',
        password_hash='hashed_password_1',
        name='Unique Test 1',
        created_at=datetime.utcnow()
    )

    session.add(user1)
    session.commit()

    # Try to create second user with same email
    user2 = User(
        email='unique_test@example.com',
        password_hash='hashed_password_2',
        name='Unique Test 2',
        created_at=datetime.utcnow()
    )

    session.add(user2)

    # Assert that exception is raised when committing
    with pytest.raises(Exception) as excinfo:
        session.commit()

    # Check that the error is related to unique constraint
    assert "unique constraint" in str(excinfo.value).lower() or "UNIQUE constraint failed" in str(excinfo.value)

    # Rollback to clean the session
    session.rollback()


def test_user_representation(session):
    """Test the string representation of User."""
    user = User(
        email='repr_test@example.com',
        password_hash='hashed_password',
        name='Repr Test',
        created_at=datetime.utcnow()
    )

    session.add(user)
    session.commit()

    # Check string representation
    assert str(user) == f"User(id={user.id}, email='repr_test@example.com', name='Repr Test')"
    assert repr(user) == f"User(id={user.id}, email='repr_test@example.com', name='Repr Test')"


def test_user_properties(session):
    """Test additional User properties and methods."""
    user = User(
        email='properties_test@example.com',
        password_hash='hashed_password',
        name='Properties Test',
        created_at=datetime.utcnow(),
        is_active=True
    )

    session.add(user)
    session.commit()

    # Test is_active property
    assert user.is_active is True

    # Deactivate user
    user.is_active = False
    session.commit()

    # Refresh from database
    session.refresh(user)
    assert user.is_active is False