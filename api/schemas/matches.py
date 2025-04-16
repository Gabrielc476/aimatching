"""
Match schemas for the API.

This module defines schemas for job-resume match-related requests and responses.
"""
from marshmallow import fields, validate, validates, ValidationError, validates_schema

from . import ma
from .jobs import JobSchema
from .resumes import ResumeSchema


class MatchSchema(ma.Schema):
    """Schema for match responses."""
    id = fields.Integer()
    user_id = fields.Integer()
    job_id = fields.Integer()
    resume_id = fields.Integer()
    score = fields.Float()
    match_details = fields.Dict()
    created_at = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")
    status = fields.String()

    class Meta:
        """Meta options for the schema."""
        fields = (
            'id', 'user_id', 'job_id', 'resume_id', 'score',
            'match_details', 'created_at', 'status'
        )


class MatchDetailSchema(MatchSchema):
    """Schema for detailed match responses including job and resume."""
    job = fields.Nested(JobSchema)
    resume = fields.Nested(ResumeSchema)

    class Meta(MatchSchema.Meta):
        """Meta options for the schema."""
        fields = MatchSchema.Meta.fields + ('job', 'resume')


class MatchAnalysisSchema(ma.Schema):
    """Schema for match analysis requests."""
    job_id = fields.Integer(required=False)
    resume_id = fields.Integer(required=False)
    job_data = fields.Dict(required=False)
    resume_data = fields.Dict(required=False)

    class Meta:
        """Meta options for the schema."""
        fields = ('job_id', 'resume_id', 'job_data', 'resume_data')

    @validates_schema
    def validate_sources(self, data, **kwargs):
        """Validate job and resume sources"""
        # Validate job sources
        if data.get('job_id') is not None and data.get('job_data') is not None:
            raise ValidationError("Cannot provide both job_id and job_data")

        # Validate resume sources
        if data.get('resume_id') is not None and data.get('resume_data') is not None:
            raise ValidationError("Cannot provide both resume_id and resume_data")

        # Validate at least one job source is provided
        if data.get('job_id') is None and data.get('job_data') is None:
            raise ValidationError("Either job_id or job_data must be provided")

        # Validate at least one resume source is provided
        if data.get('resume_id') is None and data.get('resume_data') is None:
            raise ValidationError("Either resume_id or resume_data must be provided")


class MatchListSchema(ma.Schema):
    """Schema for match list responses."""
    matches = fields.List(fields.Nested(MatchDetailSchema))
    total = fields.Integer()
    page = fields.Integer()
    per_page = fields.Integer()
    total_pages = fields.Integer()

    class Meta:
        """Meta options for the schema."""
        fields = ('matches', 'total', 'page', 'per_page', 'total_pages')


class MatchRecommendationSchema(ma.Schema):
    """Schema for match recommendation responses."""
    match_id = fields.Integer()
    score = fields.Float()
    strengths = fields.List(fields.Dict())
    gaps = fields.List(fields.Dict())
    recommendations = fields.List(fields.Dict())

    class Meta:
        """Meta options for the schema."""
        fields = ('match_id', 'score', 'strengths', 'gaps', 'recommendations')


# Instantiate schemas
match_schema = MatchSchema()
matches_schema = MatchSchema(many=True)
match_detail_schema = MatchDetailSchema()
match_list_schema = MatchListSchema()
match_analysis_schema = MatchAnalysisSchema()
match_recommendation_schema = MatchRecommendationSchema()