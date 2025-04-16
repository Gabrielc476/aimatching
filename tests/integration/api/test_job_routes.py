"""
Tests for job API routes.
"""

import pytest
import json
from datetime import datetime, timedelta


def test_get_jobs(client, auth_headers, test_jobs):
    """Test getting a list of jobs."""
    # Send request to get jobs
    response = client.get(
        '/api/jobs',
        headers=auth_headers
    )

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'jobs' in data
    assert isinstance(data['jobs'], list)
    assert len(data['jobs']) > 0

    # Check job structure
    job = data['jobs'][0]
    assert 'id' in job
    assert 'title' in job
    assert 'company' in job
    assert 'location' in job
    assert 'job_type' in job
    assert 'experience_level' in job
    assert 'skills' in job


def test_get_jobs_pagination(client, auth_headers, test_jobs):
    """Test pagination for jobs list."""
    # Send request for first page with limit=2
    response = client.get(
        '/api/jobs?page=1&limit=2',
        headers=auth_headers
    )

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'jobs' in data
    assert len(data['jobs']) <= 2
    assert 'pagination' in data
    assert 'total' in data['pagination']
    assert 'page' in data['pagination']
    assert 'limit' in data['pagination']
    assert 'pages' in data['pagination']
    assert data['pagination']['page'] == 1
    assert data['pagination']['limit'] == 2

    # Store first page results
    first_page_jobs = data['jobs']

    # Send request for second page
    response = client.get(
        '/api/jobs?page=2&limit=2',
        headers=auth_headers
    )

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'jobs' in data
    assert data['pagination']['page'] == 2

    # Verify second page has different jobs than first page
    if len(data['jobs']) > 0 and len(first_page_jobs) > 0:
        second_page_jobs = data['jobs']
        assert second_page_jobs[0]['id'] != first_page_jobs[0]['id']


def test_get_job_by_id(client, auth_headers, test_jobs):
    """Test getting a specific job by ID."""
    # Get a test job
    test_job = test_jobs[0]

    # Send request to get the job
    response = client.get(
        f'/api/jobs/{test_job.id}',
        headers=auth_headers
    )

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'job' in data
    assert data['job']['id'] == test_job.id
    assert data['job']['title'] == test_job.title
    assert data['job']['company'] == test_job.company
    assert data['job']['linkedin_id'] == test_job.linkedin_id

    # Check that we get full job details
    assert 'description' in data['job']
    assert 'requirements' in data['job']
    assert 'skills' in data['job']
    assert 'url' in data['job']


def test_get_nonexistent_job(client, auth_headers):
    """Test requesting a job that doesn't exist."""
    # Send request for a non-existent job ID
    response = client.get(
        '/api/jobs/999999',
        headers=auth_headers
    )

    # Check response
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data


def test_search_jobs(client, auth_headers, test_jobs, session):
    """Test searching for jobs."""
    # Create jobs with specific attributes for search testing
    from models.job import Job

    # Create a job with specific title and skills
    search_job = Job(
        linkedin_id='search_specific_job',
        title='Senior Python Engineer',
        company='Search Test Company',
        location='Remote, Brazil',
        description='We are looking for a Senior Python Engineer.',
        job_type='full-time',
        experience_level='senior',
        skills=['Python', 'Flask', 'AWS', 'Docker'],
        url='https://linkedin.com/jobs/search_specific_job',
        posted_at=datetime.utcnow(),
        scraped_at=datetime.utcnow(),
        is_active=True
    )

    session.add(search_job)
    session.commit()

    # Search by keyword in title
    response = client.post(
        '/api/jobs/search',
        data=json.dumps({
            'keywords': ['Python', 'Engineer']
        }),
        content_type='application/json',
        headers=auth_headers
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'jobs' in data
    assert len(data['jobs']) > 0
    assert any(job['title'] == 'Senior Python Engineer' for job in data['jobs'])

    # Search by location
    response = client.post(
        '/api/jobs/search',
        data=json.dumps({
            'location': 'Remote'
        }),
        content_type='application/json',
        headers=auth_headers
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'jobs' in data
    assert len(data['jobs']) > 0
    assert any(job['location'] == 'Remote, Brazil' for job in data['jobs'])

    # Search by experience level
    response = client.post(
        '/api/jobs/search',
        data=json.dumps({
            'experience_level': 'senior'
        }),
        content_type='application/json',
        headers=auth_headers
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'jobs' in data
    assert any(job['experience_level'] == 'senior' for job in data['jobs'])

    # Search by skills
    response = client.post(
        '/api/jobs/search',
        data=json.dumps({
            'skills': ['Flask', 'AWS']
        }),
        content_type='application/json',
        headers=auth_headers
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'jobs' in data

    # Combined search
    response = client.post(
        '/api/jobs/search',
        data=json.dumps({
            'keywords': ['Python'],
            'experience_level': 'senior',
            'job_type': 'full-time',
            'skills': ['AWS']
        }),
        content_type='application/json',
        headers=auth_headers
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'jobs' in data
    assert any(job['linkedin_id'] == 'search_specific_job' for job in data['jobs'])


def test_get_jobs_unauthorized(client):
    """Test accessing jobs without authentication."""
    # Send request without auth headers
    response = client.get('/api/jobs')

    # Check response
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data


def test_get_job_matches(client, auth_headers, test_user, test_matches):
    """Test getting job matches for the authenticated user."""
    # Send request to get matches
    response = client.get(
        '/api/jobs/matches',
        headers=auth_headers
    )

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'matches' in data
    assert isinstance(data['matches'], list)
    assert len(data['matches']) > 0

    # Check match structure
    match = data['matches'][0]
    assert 'id' in match
    assert 'job' in match
    assert 'score' in match
    assert 'status' in match
    assert 'job_id' in match
    assert 'created_at' in match
    assert match['user_id'] == test_user.id

    # Check included job details
    assert 'title' in match['job']
    assert 'company' in match['job']
    assert 'location' in match['job']


def test_get_job_matches_with_filters(client, auth_headers, test_user, test_matches):
    """Test getting job matches with filters."""
    # Send request for high score matches
    response = client.get(
        '/api/jobs/matches?min_score=85',
        headers=auth_headers
    )

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'matches' in data
    assert all(match['score'] >= 85 for match in data['matches'])

    # Send request for matches with specific status
    response = client.get(
        '/api/jobs/matches?status=new',
        headers=auth_headers
    )

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'matches' in data
    assert all(match['status'] == 'new' for match in data['matches'])


def test_get_match_details(client, auth_headers, test_matches):
    """Test getting detailed information about a specific match."""
    # Get a test match
    test_match = test_matches[0]

    # Send request to get match details
    response = client.get(
        f'/api/match/{test_match.id}',
        headers=auth_headers
    )

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'match' in data
    assert data['match']['id'] == test_match.id
    assert data['match']['score'] == test_match.score
    assert data['match']['job_id'] == test_match.job_id

    # Check that we get full match details
    assert 'match_details' in data['match']
    assert 'skills_match' in data['match']['match_details']
    assert 'recommendations' in data['match']['match_details']

    # Check that we get job information
    assert 'job' in data
    assert data['job']['id'] == test_match.job_id
    assert 'title' in data['job']
    assert 'company' in data['job']
    assert 'description' in data['job']
    assert 'skills' in data['job']


def test_update_match_status(client, auth_headers, test_matches):
    """Test updating the status of a match."""
    # Get a test match
    test_match = test_matches[0]
    assert test_match.status == 'new'  # Initial status

    # Send request to update status to 'viewed'
    response = client.put(
        f'/api/match/{test_match.id}/status',
        data=json.dumps({
            'status': 'viewed'
        }),
        content_type='application/json',
        headers=auth_headers
    )

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'match' in data
    assert data['match']['status'] == 'viewed'

    # Verify status was updated in database
    response = client.get(
        f'/api/match/{test_match.id}',
        headers=auth_headers
    )

    data = json.loads(response.data)
    assert data['match']['status'] == 'viewed'