"""
Job schemas for the API.

This module defines schemas for job-related requests and responses.
"""
from marshmallow import fields, validate, validates, ValidationError

from . import ma


class JobSchema(ma.Schema):
    """Schema for job responses."""
    id = fields.Integer()
    linkedin_id = fields.String()
    title = fields.String()
    company = fields.String()
    location = fields.String()
    description = fields.String()
    requirements = fields.Dict()
    salary_range = fields.String()
    job_type = fields.String()
    experience_level = fields.String()
    skills = fields.List(fields.String())
    url = fields.URL()
    posted_at = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")
    scraped_at = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")
    is_active = fields.Boolean()

    class Meta:
        """Meta options for the schema."""
        fields = (
            'id', 'linkedin_id', 'title', 'company', 'location', 'description',
            'requirements', 'salary_range', 'job_type', 'experience_level',
            'skills', 'url', 'posted_at', 'scraped_at', 'is_active'
        )


class JobListSchema(ma.Schema):
    """Schema for job list responses."""
    jobs = fields.List(fields.Nested(JobSchema))
    total = fields.Integer()
    page = fields.Integer()
    per_page = fields.Integer()
    total_pages = fields.Integer()

    class Meta:
        """Meta options for the schema."""
        fields = ('jobs', 'total', 'page', 'per_page', 'total_pages')


class JobSearchSchema(ma.Schema):
    """Schema for job search requests."""
    keywords = fields.String(required=False)
    location = fields.String(required=False)
    job_type = fields.String(required=False)
    experience_level = fields.String(required=False)
    skills = fields.List(fields.String(), required=False)
    salary_min = fields.Integer(required=False)
    salary_max = fields.Integer(required=False)
    posted_after = fields.DateTime(format="%Y-%m-%d", required=False)
    page = fields.Integer(missing=1)
    per_page = fields.Integer(missing=20, validate=validate.Range(min=1, max=100))

    class Meta:
        """Meta options for the schema."""
        fields = (
            'keywords', 'location', 'job_type', 'experience_level',
            'skills', 'salary_min', 'salary_max', 'posted_after',
            'page', 'per_page'
        )


# Instantiate schemas
job_schema = JobSchema()
jobs_schema = JobSchema(many=True)
job_list_schema = JobListSchema()
job_search_schema = JobSearchSchema()