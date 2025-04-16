"""
Profile schemas for the API.

This module defines schemas for profile-related requests and responses.
"""
from marshmallow import fields, validate, validates, ValidationError

from . import ma


class ProfileSchema(ma.Schema):
    """Schema for profile responses."""
    id = fields.Integer()
    user_id = fields.Integer()
    title = fields.String()
    location = fields.String()
    skills = fields.List(fields.String())
    experience_level = fields.String()
    job_preferences = fields.Dict()
    updated_at = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")

    class Meta:
        """Meta options for the schema."""
        fields = (
            'id', 'user_id', 'title', 'location', 'skills',
            'experience_level', 'job_preferences', 'updated_at'
        )


class ProfileUpdateSchema(ma.Schema):
    """Schema for profile update requests."""
    title = fields.String(required=False)
    location = fields.String(required=False)
    skills = fields.List(fields.String(), required=False)
    experience_level = fields.String(required=False)
    job_preferences = fields.Dict(required=False)

    class Meta:
        """Meta options for the schema."""
        fields = (
            'title', 'location', 'skills', 'experience_level', 'job_preferences'
        )


# Instantiate schemas
profile_schema = ProfileSchema()
profile_update_schema = ProfileUpdateSchema()