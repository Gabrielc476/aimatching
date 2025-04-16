"""
Tests for Job model.
"""

import pytest
from datetime import datetime, timedelta
from models.job import Job


def test_job_creation(session):
    """Test Job model creation."""
    # Create job
    job = Job(
        linkedin_id='test_job_123',
        title='Test Job Position',
        company='Test Company Inc.',
        location='Remote, Brazil',
        description='This is a test job description.',
        requirements={'experience': '3+ years', 'education': "Bachelor's degree"},
        salary_range='R$10,000 - R$15,000',
        job_type='full-time',
        experience_level='mid-level',
        skills=['Python', 'Flask', 'PostgreSQL'],
        url='https://linkedin.com/jobs/test_job_123',
        posted_at=datetime.utcnow() - timedelta(days=1),
        scraped_at=datetime.utcnow(),
        is_active=True
    )

    session.add(job)
    session.commit()

    # Query job
    retrieved_job = session.query(Job).filter_by(linkedin_id='test_job_123').first()

    # Assert job was created correctly
    assert retrieved_job is not None
    assert retrieved_job.linkedin_id == 'test_job_123'
    assert retrieved_job.title == 'Test Job Position'
    assert retrieved_job.company == 'Test Company Inc.'
    assert retrieved_job.location == 'Remote, Brazil'
    assert retrieved_job.description == 'This is a test job description.'
    assert retrieved_job.requirements == {'experience': '3+ years', 'education': "Bachelor's degree"}
    assert retrieved_job.salary_range == 'R$10,000 - R$15,000'
    assert retrieved_job.job_type == 'full-time'
    assert retrieved_job.experience_level == 'mid-level'
    assert retrieved_job.skills == ['Python', 'Flask', 'PostgreSQL']
    assert retrieved_job.url == 'https://linkedin.com/jobs/test_job_123'
    assert retrieved_job.posted_at is not None
    assert retrieved_job.scraped_at is not None
    assert retrieved_job.is_active is True


def test_job_unique_linkedin_id_constraint(session):
    """Test that jobs must have unique LinkedIn IDs."""
    # Create first job
    job1 = Job(
        linkedin_id='unique_test_job_123',
        title='Unique Test Job 1',
        company='Test Company Inc.',
        location='Remote, Brazil',
        description='This is a test job description.',
        url='https://linkedin.com/jobs/unique_test_job_123',
        scraped_at=datetime.utcnow(),
    )

    session.add(job1)
    session.commit()

    # Try to create second job with same LinkedIn ID
    job2 = Job(
        linkedin_id='unique_test_job_123',
        title='Unique Test Job 2',
        company='Different Company Ltd.',
        location='São Paulo, Brazil',
        description='This is another test job description.',
        url='https://linkedin.com/jobs/unique_test_job_123',
        scraped_at=datetime.utcnow(),
    )

    session.add(job2)

    # Assert that exception is raised when committing
    with pytest.raises(Exception) as excinfo:
        session.commit()

    # Check that the error is related to unique constraint
    assert "unique constraint" in str(excinfo.value).lower() or "UNIQUE constraint failed" in str(excinfo.value)

    # Rollback to clean the session
    session.rollback()


def test_job_representation(session):
    """Test the string representation of Job."""
    job = Job(
        linkedin_id='repr_test_job_123',
        title='Repr Test Job',
        company='Repr Company',
        location='Test Location',
        url='https://linkedin.com/jobs/repr_test_job_123',
        scraped_at=datetime.utcnow(),
    )

    session.add(job)
    session.commit()

    # Check string representation
    expected_repr = f"Job(id={job.id}, title='Repr Test Job', company='Repr Company')"
    assert str(job) == expected_repr
    assert repr(job) == expected_repr


def test_job_deactivation(session):
    """Test job deactivation."""
    # Create active job
    job = Job(
        linkedin_id='deactivate_test_job_123',
        title='Deactivate Test Job',
        company='Test Company',
        location='Test Location',
        url='https://linkedin.com/jobs/deactivate_test_job_123',
        scraped_at=datetime.utcnow(),
        is_active=True
    )

    session.add(job)
    session.commit()

    # Assert job is active
    assert job.is_active is True

    # Deactivate job
    job.is_active = False
    session.commit()

    # Refresh from database
    session.refresh(job)
    assert job.is_active is False


def test_job_json_fields(session):
    """Test handling of JSON fields in the Job model."""
    # Test with different JSON data structures
    job = Job(
        linkedin_id='json_test_job_123',
        title='JSON Test Job',
        company='JSON Company',
        location='Test Location',
        url='https://linkedin.com/jobs/json_test_job_123',
        scraped_at=datetime.utcnow(),
        # Complex JSON data in requirements
        requirements={
            'experience': {
                'years': 5,
                'technologies': ['Python', 'Flask', 'SQLAlchemy']
            },
            'education': {
                'level': "Bachelor's degree",
                'fields': ['Computer Science', 'Information Technology']
            },
            'certifications': ['AWS Certified Developer', 'Scrum Master']
        },
        # Array of skills
        skills=['Python', 'Flask', 'PostgreSQL', 'Redis', 'Docker']
    )

    session.add(job)
    session.commit()

    # Query job
    retrieved_job = session.query(Job).filter_by(linkedin_id='json_test_job_123').first()

    # Assert JSON fields were stored and retrieved correctly
    assert retrieved_job.requirements['experience']['years'] == 5
    assert 'Python' in retrieved_job.requirements['experience']['technologies']
    assert 'Computer Science' in retrieved_job.requirements['education']['fields']
    assert 'AWS Certified Developer' in retrieved_job.requirements['certifications']

    assert len(retrieved_job.skills) == 5
    assert 'PostgreSQL' in retrieved_job.skills
    assert 'Docker' in retrieved_job.skills