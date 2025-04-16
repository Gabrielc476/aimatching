"""
Resume controller for the API.

This module provides controller classes for handling resume-related
requests, including upload, retrieval, and analysis.
"""
import os
from flask import request, current_app
from werkzeug.utils import secure_filename

from . import BaseController
from ..middlewares.auth import jwt_required
from ..schemas.resumes import (
    resume_schema,
    resumes_schema,
    resume_detail_schema,
    resume_upload_schema
)
from database.repositories.resume_repository import ResumeRepository
from services.matching.resume_analyzer import ResumeAnalyzer
from services.storage.file_service import FileService


class ResumeResource(BaseController):
    """Resource for resume operations."""

    def __init__(self):
        """Initialize the resume resource."""
        self.resume_repository = ResumeRepository()

    @jwt_required
    def get(self):
        """Get the current user's resumes.

        Returns:
            tuple: Response data and status code
        """
        user = self._get_current_user()

        # Check if we need to return a specific resume
        resume_id = request.args.get('id')
        if resume_id:
            try:
                resume_id = int(resume_id)
                resume = self.resume_repository.get_by_id(resume_id)

                if not resume or resume.user_id != user.id:
                    return self._error_response(
                        "Resume not found",
                        status_code=404
                    )

                return self._success_response(data=resume_detail_schema.dump(resume))
            except ValueError:
                return self._error_response("Invalid resume ID", status_code=400)

        # Get all resumes for the user
        resumes = self.resume_repository.get_by_user_id(user.id)

        return self._success_response(data=resumes_schema.dump(resumes))


class ResumeUploadResource(BaseController):
    """Resource for resume upload and analysis."""

    def __init__(self):
        """Initialize the resume upload resource."""
        self.resume_repository = ResumeRepository()
        self.resume_analyzer = ResumeAnalyzer()
        self.file_service = FileService()

    @jwt_required
    def post(self):
        """Upload and analyze a resume.

        Returns:
            tuple: Response data and status code
        """
        user = self._get_current_user()

        # Check if file is present in the request
        if 'resume' not in request.files:
            return self._error_response(
                "No resume file provided",
                status_code=400
            )

        file = request.files['resume']

        # Check if the file has a name
        if file.filename == '':
            return self._error_response(
                "No file selected",
                status_code=400
            )

        # Check if the file is allowed
        allowed_extensions = {'pdf', 'docx', 'doc', 'txt'}
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

        if file_ext not in allowed_extensions:
            return self._error_response(
                f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}",
                status_code=400
            )

        try:
            # Read the file content
            file_content = file.read()

            # Set additional parameters
            is_primary = request.form.get('is_primary', 'false').lower() == 'true'

            # Extract text from the resume
            resume_text = self.file_service.extract_text_from_resume(file_content, file_ext)

            # Analyze the resume
            analysis_result = self.resume_analyzer.analyze(resume_text)

            # Save the resume to the database
            resume = self.resume_repository.create(
                user_id=user.id,
                filename=filename,
                content_type=f"application/{file_ext}",
                content=file_content,
                parsed_content=analysis_result,
                skills=analysis_result.get('skills', []),
                experience=analysis_result.get('experience', []),
                education=analysis_result.get('education', []),
                is_primary=is_primary
            )

            # If this is set as primary, update other resumes
            if is_primary:
                self.resume_repository.set_as_primary(resume.id, user.id)

            # Queue a task to update user matches
            from tasks.matching_tasks import update_user_matches
            update_user_matches.delay(user.id)

            # Prepare response
            response_data = {
                'id': resume.id,
                'filename': resume.filename,
                'upload_success': True,
                'analysis_success': True,
                'detected_skills': resume.skills,
                'message': "Resume uploaded and analyzed successfully"
            }

            return self._success_response(
                data=response_data,
                message="Resume uploaded and analyzed successfully",
                status_code=201
            )

        except Exception as e:
            current_app.logger.error(f"Resume upload/analysis error: {str(e)}")
            return self._error_response(
                "Error processing resume file",
                status_code=500,
                payload={"error": str(e)}
            )