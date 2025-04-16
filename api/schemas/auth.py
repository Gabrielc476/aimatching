"""
Authentication schemas for the API.

This module defines schemas for authentication-related requests and responses.
"""
from marshmallow import fields, validate, validates, ValidationError

from . import ma


class RegisterSchema(ma.Schema):
    """Schema for user registration requests."""
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    name = fields.String(required=True)

    class Meta:
        """Meta options for the schema."""
        fields = ('email', 'password', 'name')


class LoginSchema(ma.Schema):
    """Schema for user login requests."""
    email = fields.Email(required=True)
    password = fields.String(required=True)

    class Meta:
        """Meta options for the schema."""
        fields = ('email', 'password')


class RefreshTokenSchema(ma.Schema):
    """Schema for token refresh requests."""
    refresh_token = fields.String(required=True)

    class Meta:
        """Meta options for the schema."""
        fields = ('refresh_token',)


class TokenSchema(ma.Schema):
    """Schema for token responses."""
    access_token = fields.String()
    refresh_token = fields.String()
    token_type = fields.String(default="Bearer")
    expires_in = fields.Integer()

    class Meta:
        """Meta options for the schema."""
        fields = ('access_token', 'refresh_token', 'token_type', 'expires_in')


class UserSchema(ma.Schema):
    """Schema for user information responses."""
    id = fields.Integer()
    email = fields.Email()
    name = fields.String()
    created_at = fields.DateTime(format="%Y-%m-%dT%H:%M:%S")

    class Meta:
        """Meta options for the schema."""
        fields = ('id', 'email', 'name', 'created_at')


# Instantiate schemas
register_schema = RegisterSchema()
login_schema = LoginSchema()
refresh_token_schema = RefreshTokenSchema()
token_schema = TokenSchema()
user_schema = UserSchema()