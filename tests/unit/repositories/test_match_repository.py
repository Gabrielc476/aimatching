"""
Tests for MatchRepository.
"""

import pytest
from datetime import datetime, timedelta
from database.repositories.match_repository import MatchRepository
from models.match import Match


def test_get_by_id(session, test_matches):
    """Test retrieving a match by ID."""
    # Initialize repository
    match_repository = MatchRepository(session)

    # Get the first test match
    test_match = test_matches[0]

    # Retrieve it using the repository
    match = match_repository.get_by_id(test_match.id)

    # Verify it's the correct match
    assert match is not None
    assert match.id == test_match.id
    assert match.user_id == test_match.user_id
    assert match.job_id == test_match.job_id
    assert match.score == test_match.score


def test_get_user_matches(session, test_user, test_matches):
    """Test retrieving matches for a specific user."""
    # Initialize repository
    match_repository = MatchRepository(session)

    # Get matches for the test user
    user_matches = match_repository.get_user_matches(test_user.id)

    # Verify correct matches were returned
    assert len(user_matches) == len(test_matches)
    assert all(match.user_id == test_user.id for match in user_matches)

    # Test with min_score filter
    high_score_matches = match_repository.get_user_matches(test_user.id, min_score=85)
    assert len(high_score_matches) < len(user_matches)
    assert all(match.score >= 85 for match in high_score_matches)

    # Test with status filter
    new_matches = match_repository.get_user_matches(test_user.id, status='new')
    assert all(match.status == 'new' for match in new_matches)


def test_get_match_by_user_and_job(session, test_user, test_jobs, test_matches):
    """Test retrieving a specific match between a user and a job."""
    # Initialize repository
    match_repository = MatchRepository(session)

    # Get the first test match
    test_match = test_matches[0]

    # Retrieve it using the repository
    match = match_repository.get_match_by_user_and_job(test_user.id, test_match.job_id)

    # Verify it's the correct match
    assert match is not None
    assert match.id == test_match.id
    assert match.user_id == test_user.id
    assert match.job_id == test_match.job_id

    # Try to retrieve a non-existent match
    non_matched_job = next(job for job in test_jobs if not any(m.job_id == job.id for m in test_matches))
    no_match = match_repository.get_match_by_user_and_job(test_user.id, non_matched_job.id)
    assert no_match is None


def test_create_or_update_match(session, test_user, test_resume, test_jobs):
    """Test creating and updating matches."""
    # Initialize repository
    match_repository = MatchRepository(session)

    # Get a job that doesn't have a match yet
    test_job = next(job for job in test_jobs if not session.query(Match).filter_by(
        user_id=test_user.id, job_id=job.id).first())

    # Create match data
    match_details = {
        'skills_match': {
            'matching': ['Python', 'SQL'],
            'missing': ['C#', 'ASP.NET']
        },
        'experience_match': 75,
        'education_match': 80,
        'overall_score': 75,
        'recommendations': [
            'Add C# to your skill set',
            'Get certified in ASP.NET'
        ]
    }

    # Create a new match
    match = match_repository.create_or_update_match(
        test_user.id, test_job.id, test_resume.id, 75, match_details
    )

    # Verify match was created correctly
    assert match is not None
    assert match.user_id == test_user.id
    assert match.job_id == test_job.id
    assert match.resume_id == test_resume.id
    assert match.score == 75
    assert match.match_details == match_details
    assert match.status == 'new'

    # Update the match
    updated_details = match_details.copy()
    updated_details['recommendations'].append('Focus on cloud technologies')

    updated_match = match_repository.create_or_update_match(
        test_user.id, test_job.id, test_resume.id, 80, updated_details
    )

    # Verify match was updated correctly
    assert updated_match.id == match.id  # Same match
    assert updated_match.score == 80  # Updated score
    assert len(updated_match.match_details['recommendations']) == 3  # Updated recommendations


def test_update_match_status(session, test_matches):
    """Test updating match status."""
    # Initialize repository
    match_repository = MatchRepository(session)

    # Get the first test match
    test_match = test_matches[0]
    assert test_match.status == 'new'  # Should be 'new' initially

    # Update the status
    success = match_repository.update_match_status(test_match.id, 'viewed')

    # Verify update was successful
    assert success is True

    # Refresh match from database
    session.refresh(test_match)
    assert test_match.status == 'viewed'

    # Try to update a non-existent match
    success = match_repository.update_match_status(999999, 'applied')
    assert success is False


def test_batch_create_matches(session, test_user, test_resume, test_jobs):
    """Test creating multiple matches in batch."""
    # Initialize repository
    match_repository = MatchRepository(session)

    # Get jobs that don't have matches yet
    test_job_ids = [job.id for job in test_jobs if not session.query(Match).filter_by(
        user_id=test_user.id, job_id=job.id).first()][:3]  # Get up to 3 jobs

    # Create match data for each job
    matches_data = []
    for i, job_id in enumerate(test_job_ids):
        score = 70 - (i * 5)  # Scores: 70, 65, 60

        match_data = {
            'user_id': test_user.id,
            'job_id': job_id,
            'resume_id': test_resume.id,
            'score': score,
            'match_details': {
                'skills_match': {
                    'matching': ['Python', 'SQL'],
                    'missing': ['Java']
                },
                'overall_score': score
            },
            'status': 'new'
        }
        matches_data.append(match_data)

    # Create matches in batch
    count = match_repository.batch_create_matches(matches_data)

    # Verify correct number of matches were created
    assert count == len(matches_data)

    # Query the created matches
    created_matches = session.query(Match).filter(
        Match.user_id == test_user.id,
        Match.job_id.in_(test_job_ids)
    ).all()

    assert len(created_matches) == len(matches_data)


def test_get_match_statistics(session, test_user, test_matches):
    """Test retrieving match statistics for a user."""
    # Initialize repository
    match_repository = MatchRepository(session)

    # Get match statistics for the test user
    stats = match_repository.get_match_statistics(test_user.id)

    # Verify statistics were calculated correctly
    assert 'total_matches' in stats
    assert stats['total_matches'] == len(test_matches)

    assert 'score_ranges' in stats
    assert 'excellent' in stats['score_ranges']  # 85-100
    assert 'good' in stats['score_ranges']  # 70-84
    assert 'average' in stats['score_ranges']  # 50-69
    assert 'low' in stats['score_ranges']  # <50

    assert 'status_counts' in stats
    assert 'new' in stats['status_counts']

    assert 'average_score' in stats
    # The average should be around 80 given our test data (90, 80, 70)
    assert stats['average_score'] >= 75
    assert stats['average_score'] <= 85