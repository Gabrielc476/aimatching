"""
Resume schemas for the API.

This module defines schemas for resume-related requests and responses.
"""
from marshmallow import fields, validate, validates, ValidationError

from . import ma


class ResumeSchema(ma.Schema):
    """Schema for resume responses."""
    id = fields.Integer()
    user_id = fields.Integer()
    filename = fields.String()
    content_type = fields.String()
    skills = fields.List(fields.String())
    experience = fields.List(fields.Dict())
    education = fields.List(fields.Dict())
    uploaded_at = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")
    is_primary = fields.Boolean()

    class Meta:
        """Meta options for the schema."""
        fields = (
            'id', 'user_id', 'filename', 'content_type', 'skills',
            'experience', 'education', 'uploaded_at', 'is_primary'
        )


class ResumeDetailSchema(ResumeSchema):
    """Schema for detailed resume responses including parsed content."""
    parsed_content = fields.Dict()

    class Meta(ResumeSchema.Meta):
        """Meta options for the schema."""
        fields = ResumeSchema.Meta.fields + ('parsed_content',)


class ResumeUploadSchema(ma.Schema):
    """Schema for resume upload responses."""
    id = fields.Integer()
    filename = fields.String()
    upload_success = fields.Boolean()
    analysis_success = fields.Boolean()
    detected_skills = fields.List(fields.String())
    message = fields.String()

    class Meta:
        """Meta options for the schema."""
        fields = (
            'id', 'filename', 'upload_success', 'analysis_success',
            'detected_skills', 'message'
        )


# Instantiate schemas
resume_schema = ResumeSchema()
resumes_schema = ResumeSchema(many=True)
resume_detail_schema = ResumeDetailSchema()
resume_upload_schema = ResumeUploadSchema()