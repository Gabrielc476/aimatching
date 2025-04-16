"""
Tests for MatchService.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from services.matching.match_service import MatchService
from services.ai.claude_service import ClaudeService
from models.resume import Resume
from models.job import Job


@pytest.fixture
def claude_service_mock():
    """Mock Claude service for testing."""
    mock = Mock(spec=ClaudeService)

    # Mock calculate_match method
    mock.calculate_match.return_value = {
        "compatibility": {
            "skills_technical": 85,
            "experience": 75,
            "education": 90,
            "overall": 80
        },
        "analysis": {
            "matching_skills": ["Python", "SQL", "AWS"],
            "missing_skills": ["Docker", "Kubernetes"],
            "experience_match": "Good match for required experience",
            "education_match": "Education requirements met"
        },
        "recommendations": [
            "Add Docker and Kubernetes to your skill set",
            "Highlight cloud infrastructure experience"
        ]
    }

    return mock


@pytest.fixture
def match_service(claude_service_mock):
    """Initialize MatchService with mocked dependencies."""
    return MatchService(claude_service_mock)


def test_calculate_match(match_service, claude_service_mock, test_resume, test_jobs):
    """Test calculating match between resume and job."""
    # Get a test job
    test_job = test_jobs[0]

    # Calculate match
    match_result = match_service.calculate_match(test_resume, test_job)

    # Verify Claude service was called correctly
    claude_service_mock.calculate_match.assert_called_once()
    args, _ = claude_service_mock.calculate_match.call_args
    assert args[0] == test_resume
    assert args[1] == test_job

    # Verify match result
    assert 'score' in match_result
    assert match_result['score'] == 80  # From mock return value

    assert 'details' in match_result
    assert 'skills_match' in match_result['details']
    assert 'experience_match' in match_result['details']
    assert 'education_match' in match_result['details']
    assert 'recommendations' in match_result['details']


def test_normalize_score(match_service):
    """Test score normalization."""
    # Test within the normal range
    assert match_service._normalize_score(75) == 75

    # Test scores at boundaries
    assert match_service._normalize_score(0) == 0
    assert match_service._normalize_score(100) == 100

    # Test scores outside boundaries
    assert match_service._normalize_score(-10) == 0
    assert match_service._normalize_score(110) == 100


def test_analyze_skills_match(match_service):
    """Test analyzing skills match between resume and job."""
    # Create test data
    resume_skills = ["Python", "JavaScript", "SQL", "AWS", "React"]
    job_skills = ["Python", "Django", "SQL", "Docker", "Git"]

    # Analyze skills match
    matching, missing, match_percentage = match_service._analyze_skills_match(resume_skills, job_skills)

    # Verify results
    assert "Python" in matching
    assert "SQL" in matching
    assert "Django" in missing
    assert "Docker" in missing
    assert "Git" in missing

    # 2 out of 5 job skills match, so expected percentage is 40%
    assert match_percentage == 40


def test_get_match_score_category(match_service):
    """Test categorizing match scores."""
    # Test excellent match
    assert match_service.get_match_score_category(90) == "excellent"
    assert match_service.get_match_score_category(85) == "excellent"

    # Test good match
    assert match_service.get_match_score_category(80) == "good"
    assert match_service.get_match_score_category(70) == "good"

    # Test average match
    assert match_service.get_match_score_category(65) == "average"
    assert match_service.get_match_score_category(50) == "average"

    # Test low match
    assert match_service.get_match_score_category(45) == "low"
    assert match_service.get_match_score_category(20) == "low"


@patch('services.matching.match_service.JobRepository')
def test_find_recommended_jobs(mock_job_repo, match_service, session, test_user, test_resume):
    """Test finding recommended jobs based on user preferences."""
    # Setup mock repository
    mock_repo_instance = MagicMock()
    mock_job_repo.return_value = mock_repo_instance

    # Create test jobs
    test_job1 = Job(
        id=101,
        linkedin_id='rec_test_1',
        title='Recommended Job 1',
        company='Rec Company',
        experience_level='mid-level',
        skills=['Python', 'Flask', 'PostgreSQL'],
        is_active=True
    )

    test_job2 = Job(
        id=102,
        linkedin_id='rec_test_2',
        title='Recommended Job 2',
        company='Another Company',
        experience_level='senior',
        skills=['Java', 'Spring', 'Hibernate'],
        is_active=True
    )

    # Mock search_jobs to return test jobs
    mock_repo_instance.search_jobs.return_value = [test_job1, test_job2]

    # Setup user preferences
    preferences = {
        'job_types': ['full-time'],
        'locations': ['Remote', 'São Paulo'],
        'experience_level': 'mid-level'
    }

    # Find recommended jobs
    recommended_jobs = match_service.find_recommended_jobs(
        user_id=test_user.id,
        resume=test_resume,
        preferences=preferences,
        preferred_skills=['Python', 'Flask'],
        count=5
    )

    # Verify job repository was called correctly
    mock_repo_instance.search_jobs.assert_called_once()
    _, kwargs = mock_repo_instance.search_jobs.call_args
    assert kwargs.get('experience_level') == 'mid-level'
    assert 'Python' in kwargs.get('skills', [])
    assert 'Flask' in kwargs.get('skills', [])

    # Verify results
    assert len(recommended_jobs) == 2
    assert recommended_jobs[0].id == 101
    assert recommended_jobs[1].id == 102


def test_match_service_integration(session, test_resume, test_jobs):
    """Integration test for MatchService with real Claude service."""
    # This test requires a real Claude API key, so we'll mock the API calls
    with patch('services.ai.claude_service.requests.post') as mock_post:
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'content': [
                {
                    'type': 'text',
                    'text': '{"compatibility":{"skills_technical":85,"experience":75,"education":90,"overall":80},"analysis":{"matching_skills":["Python","SQL","AWS"],"missing_skills":["Docker","Kubernetes"],"experience_match":"Good match for required experience","education_match":"Education requirements met"},"recommendations":["Add Docker and Kubernetes to your skill set","Highlight cloud infrastructure experience"]}'
                }
            ]
        }
        mock_post.return_value = mock_response

        # Initialize real services
        claude_service = ClaudeService("fake_api_key")
        match_service = MatchService(claude_service)

        # Get a test job
        test_job = test_jobs[0]

        # Calculate match
        match_result = match_service.calculate_match(test_resume, test_job)

        # Verify match result
        assert 'score' in match_result
        assert 'details' in match_result
        assert 'skills_match' in match_result['details']
        assert 'recommendations' in match_result['details']