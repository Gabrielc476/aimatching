"""
Match controller for the API.

This module provides controller classes for handling match-related
requests, including match analysis and recommendations.
"""
from flask import request, current_app

from . import BaseController
from ..middlewares.auth import jwt_required
from ..schemas.matches import (
    match_schema,
    match_analysis_schema,
    match_recommendation_schema
)
from database.repositories.job_repository import JobRepository
from database.repositories.resume_repository import ResumeRepository
from database.repositories.match_repository import MatchRepository
from services.matching.match_service import MatchService


class MatchAnalysisResource(BaseController):
    """Resource for match analysis."""

    def __init__(self):
        """Initialize the match analysis resource."""
        self.job_repository = JobRepository()
        self.resume_repository = ResumeRepository()
        self.match_repository = MatchRepository()
        self.match_service = MatchService()

    @jwt_required
    def post(self):
        """Analyze the match between a resume and a job.

        Returns:
            tuple: Response data and status code
        """
        user = self._get_current_user()
        data = self._validate_schema(match_analysis_schema, request.json)

        job_id = data.get('job_id')
        resume_id = data.get('resume_id')
        job_data = data.get('job_data')
        resume_data = data.get('resume_data')

        # Get job data
        if job_id:
            job = self.job_repository.get_by_id(job_id)
            if not job:
                return self._error_response(
                    "Job not found",
                    status_code=404
                )
            job_data = {
                'title': job.title,
                'company': job.company,
                'description': job.description,
                'requirements': job.requirements,
                'skills': job.skills
            }
        elif not job_data:
            return self._error_response(
                "Either job_id or job_data must be provided",
                status_code=400
            )

        # Get resume data
        if resume_id:
            resume = self.resume_repository.get_by_id(resume_id)
            if not resume or resume.user_id != user.id:
                return self._error_response(
                    "Resume not found",
                    status_code=404
                )
            resume_data = resume.parsed_content
        elif not resume_data:
            # Try to get the primary resume
            resume = self.resume_repository.get_primary_by_user_id(user.id)
            if not resume:
                return self._error_response(
                    "No resume found. Please upload a resume or provide resume_data",
                    status_code=400
                )
            resume_id = resume.id
            resume_data = resume.parsed_content

        # Analyze the match
        match_result = self.match_service.calculate_match(resume_data, job_data)

        # Save the match if both job_id and resume_id are provided
        if job_id and resume_id:
            # Check if match already exists
            existing_match = self.match_repository.get_by_job_and_resume(job_id, resume_id)

            if existing_match:
                # Update the existing match
                match = self.match_repository.update(
                    existing_match.id,
                    score=match_result['overall_score'],
                    match_details=match_result
                )
            else:
                # Create a new match
                match = self.match_repository.create(
                    user_id=user.id,
                    job_id=job_id,
                    resume_id=resume_id,
                    score=match_result['overall_score'],
                    match_details=match_result
                )

        return self._success_response(data=match_result)


class MatchRecommendationsResource(BaseController):
    """Resource for match recommendations."""

    def __init__(self):
        """Initialize the match recommendations resource."""
        self.match_repository = MatchRepository()
        self.match_service = MatchService()

    @jwt_required
    def get(self):
        """Get recommendations to improve matches.

        Returns:
            tuple: Response data and status code
        """
        user = self._get_current_user()
        match_id = request.args.get('match_id')

        if not match_id:
            return self._error_response(
                "match_id is required",
                status_code=400
            )

        try:
            match_id = int(match_id)
            match = self.match_repository.get_by_id(match_id)

            if not match or match.user_id != user.id:
                return self._error_response(
                    "Match not found",
                    status_code=404
                )

            # Generate recommendations based on the match
            recommendations = self.match_service.generate_recommendations(match)

            # Prepare response
            response_data = {
                'match_id': match.id,
                'score': match.score,
                'strengths': recommendations.get('strengths', []),
                'gaps': recommendations.get('gaps', []),
                'recommendations': recommendations.get('recommendations', [])
            }

            return self._success_response(data=response_data)

        except ValueError:
            return self._error_response("Invalid match ID", status_code=400)