"""
Tests for JobRepository.
"""

import pytest
from datetime import datetime, timedelta
from database.repositories.job_repository import JobRepository
from models.job import Job


def test_get_by_id(session, test_jobs):
    """Test retrieving a job by ID."""
    # Initialize repository
    job_repository = JobRepository(session)

    # Get the first test job
    test_job = test_jobs[0]

    # Retrieve it using the repository
    job = job_repository.get_by_id(test_job.id)

    # Verify it's the correct job
    assert job is not None
    assert job.id == test_job.id
    assert job.title == test_job.title
    assert job.company == test_job.company


def test_get_by_linkedin_id(session, test_jobs):
    """Test retrieving a job by LinkedIn ID."""
    # Initialize repository
    job_repository = JobRepository(session)

    # Get the first test job
    test_job = test_jobs[0]

    # Retrieve it using the repository
    job = job_repository.get_by_linkedin_id(test_job.linkedin_id)

    # Verify it's the correct job
    assert job is not None
    assert job.id == test_job.id
    assert job.linkedin_id == test_job.linkedin_id
    assert job.title == test_job.title


def test_save_or_update_new_job(session):
    """Test saving a new job."""
    # Initialize repository
    job_repository = JobRepository(session)

    # Create job data
    job_data = {
        'linkedin_id': 'new_test_job_456',
        'title': 'New Test Job',
        'company': 'New Company Inc.',
        'location': 'Remote, Brazil',
        'description': 'This is a new test job description.',
        'requirements': {'experience': '2+ years'},
        'salary_range': 'R$8,000 - R$12,000',
        'job_type': 'full-time',
        'experience_level': 'entry-level',
        'skills': ['JavaScript', 'React', 'Node.js'],
        'url': 'https://linkedin.com/jobs/new_test_job_456',
        'posted_at': datetime.utcnow() - timedelta(days=1),
        'is_active': True
    }

    # Save the job
    job = job_repository.save_or_update(job_data)

    # Verify the job was saved correctly
    assert job is not None
    assert job.linkedin_id == 'new_test_job_456'
    assert job.title == 'New Test Job'
    assert job.company == 'New Company Inc.'
    assert len(job.skills) == 3
    assert 'React' in job.skills
    assert job.scraped_at is not None  # Should be set automatically


def test_save_or_update_existing_job(session, test_jobs):
    """Test updating an existing job."""
    # Initialize repository
    job_repository = JobRepository(session)

    # Get the first test job
    test_job = test_jobs[0]

    # Create updated job data
    job_data = {
        'linkedin_id': test_job.linkedin_id,
        'title': 'Updated Job Title',
        'description': 'Updated job description.',
        'skills': ['Python', 'Django', 'PostgreSQL', 'Redis']
    }

    # Update the job
    updated_job = job_repository.save_or_update(job_data)

    # Verify the job was updated correctly
    assert updated_job is not None
    assert updated_job.id == test_job.id
    assert updated_job.linkedin_id == test_job.linkedin_id
    assert updated_job.title == 'Updated Job Title'
    assert updated_job.description == 'Updated job description.'
    assert len(updated_job.skills) == 4
    assert 'Django' in updated_job.skills
    assert updated_job.company == test_job.company  # Unchanged field
    assert updated_job.scraped_at > test_job.scraped_at  # Should be updated


def test_get_recent_jobs(session, test_jobs):
    """Test retrieving recent jobs."""
    # Initialize repository
    job_repository = JobRepository(session)

    # Set different posting dates for test jobs
    for i, job in enumerate(test_jobs):
        job.posted_at = datetime.utcnow() - timedelta(days=i)

    session.commit()

    # Get recent jobs (last 2 days)
    recent_jobs = job_repository.get_recent_jobs(days=2, limit=10)

    # Verify only jobs from the last 2 days are returned
    assert len(recent_jobs) <= len(test_jobs)
    for job in recent_jobs:
        assert (datetime.utcnow() - job.posted_at).days <= 2


def test_search_jobs(session, test_jobs):
    """Test searching jobs with filters."""
    # Initialize repository
    job_repository = JobRepository(session)

    # Create specific test jobs for search
    job1 = Job(
        linkedin_id='search_test_1',
        title='Senior Python Developer',
        company='Search Company',
        location='São Paulo, Brazil',
        description='Looking for an experienced Python developer.',
        job_type='full-time',
        experience_level='senior',
        skills=['Python', 'Django', 'PostgreSQL'],
        url='https://linkedin.com/jobs/search_test_1',
        posted_at=datetime.utcnow(),
        scraped_at=datetime.utcnow(),
        is_active=True
    )

    job2 = Job(
        linkedin_id='search_test_2',
        title='Junior Frontend Developer',
        company='Search Company',
        location='Rio de Janeiro, Brazil',
        description='Looking for a frontend developer with React experience.',
        job_type='full-time',
        experience_level='junior',
        skills=['JavaScript', 'React', 'CSS'],
        url='https://linkedin.com/jobs/search_test_2',
        posted_at=datetime.utcnow(),
        scraped_at=datetime.utcnow(),
        is_active=True
    )

    job3 = Job(
        linkedin_id='search_test_3',
        title='DevOps Engineer',
        company='Different Company',
        location='Remote, Brazil',
        description='Looking for a DevOps engineer with AWS experience.',
        job_type='contract',
        experience_level='mid-level',
        skills=['AWS', 'Docker', 'Kubernetes', 'Terraform'],
        url='https://linkedin.com/jobs/search_test_3',
        posted_at=datetime.utcnow(),
        scraped_at=datetime.utcnow(),
        is_active=True
    )

    session.add_all([job1, job2, job3])
    session.commit()

    # Test search by keywords
    results = job_repository.search_jobs(keywords=['python', 'developer'])
    assert len(results) >= 1
    assert any(job.linkedin_id == 'search_test_1' for job in results)

    # Test search by location
    results = job_repository.search_jobs(location='Rio')
    assert len(results) >= 1
    assert any(job.linkedin_id == 'search_test_2' for job in results)

    # Test search by job type
    results = job_repository.search_jobs(job_type='contract')
    assert len(results) >= 1
    assert any(job.linkedin_id == 'search_test_3' for job in results)

    # Test search by experience level
    results = job_repository.search_jobs(experience_level='junior')
    assert len(results) >= 1
    assert any(job.linkedin_id == 'search_test_2' for job in results)

    # Test search by skills
    results = job_repository.search_jobs(skills=['AWS', 'Docker'])
    assert len(results) >= 1
    assert any(job.linkedin_id == 'search_test_3' for job in results)

    # Test combined search
    results = job_repository.search_jobs(
        keywords=['developer'],
        location='São Paulo',
        experience_level='senior'
    )
    assert len(results) >= 1
    assert any(job.linkedin_id == 'search_test_1' for job in results)


def test_deactivate_old_jobs(session):
    """Test deactivating old jobs."""
    # Initialize repository
    job_repository = JobRepository(session)

    # Create jobs with different scraped_at dates
    job1 = Job(
        linkedin_id='deactivate_test_1',
        title='Recent Job',
        company='Test Company',
        url='https://linkedin.com/jobs/deactivate_test_1',
        scraped_at=datetime.utcnow(),
        is_active=True
    )

    job2 = Job(
        linkedin_id='deactivate_test_2',
        title='Old Job',
        company='Test Company',
        url='https://linkedin.com/jobs/deactivate_test_2',
        scraped_at=datetime.utcnow() - timedelta(days=40),  # Very old
        is_active=True
    )

    job3 = Job(
        linkedin_id='deactivate_test_3',
        title='Somewhat Old Job',
        company='Test Company',
        url='https://linkedin.com/jobs/deactivate_test_3',
        scraped_at=datetime.utcnow() - timedelta(days=20),  # Somewhat old
        is_active=True
    )

    session.add_all([job1, job2, job3])
    session.commit()

    # Deactivate jobs older than 30 days
    count = job_repository.deactivate_old_jobs(days=30)

    # Verify only the old job was deactivated
    assert count >= 1

    # Refresh jobs from database
    session.refresh(job1)
    session.refresh(job2)
    session.refresh(job3)

    assert job1.is_active is True  # Recent job should still be active
    assert job2.is_active is False  # Very old job should be deactivated
    assert job3.is_active is True  # Somewhat old job should still be active


def test_get_top_companies_by_job_count(session):
    """Test getting top companies by job count."""
    # Initialize repository
    job_repository = JobRepository(session)

    # Create jobs for different companies
    companies = ['Top Company', 'Top Company', 'Top Company',
                 'Second Company', 'Second Company',
                 'Third Company']

    for i, company in enumerate(companies):
        job = Job(
            linkedin_id=f'company_test_{i}',
            title=f'Job {i}',
            company=company,
            url=f'https://linkedin.com/jobs/company_test_{i}',
            scraped_at=datetime.utcnow(),
            is_active=True
        )
        session.add(job)

    session.commit()

    # Get top companies
    top_companies = job_repository.get_top_companies_by_job_count(limit=3)

    # Verify results
    assert len(top_companies) <= 3
    assert top_companies[0]['company'] == 'Top Company'
    assert top_companies[0]['job_count'] >= 3
    assert top_companies[1]['company'] == 'Second Company'
    assert top_companies[1]['job_count'] >= 2