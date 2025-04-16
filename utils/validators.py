"""
Validation utilities for LinkedIn Job Matcher.
"""

import re
from typing import Tuple, Any, Dict, List, Optional
import validators
from email_validator import validate_email as validate_email_lib, EmailNotValidError


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate an email address.

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"

    try:
        validate_email_lib(email)
        return True, None
    except EmailNotValidError as e:
        return False, str(e)


def validate_password(password: str, min_length: int = 8) -> Tuple[bool, Optional[str]]:
    """
    Validate a password.

    Args:
        password: Password to validate
        min_length: Minimum password length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"

    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long"

    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"

    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    return True, None


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a URL.

    Args:
        url: URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL is required"

    if not validators.url(url):
        return False, "Invalid URL format"

    return True, None


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, Optional[Dict[str, str]]]:
    """
    Validate that all required fields are present in the data.

    Args:
        data: Dictionary of data to validate
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, error_dict)
    """
    errors = {}

    for field in required_fields:
        if field not in data or data[field] is None or (isinstance(data[field], str) and data[field].strip() == ''):
            errors[field] = f"{field} is required"

    if errors:
        return False, errors

    return True, None


def validate_length(value: str, field_name: str, min_length: int = None, max_length: int = None) -> Tuple[
    bool, Optional[str]]:
    """
    Validate the length of a string.

    Args:
        value: String to validate
        field_name: Name of the field (for error message)
        min_length: Minimum allowed length (optional)
        max_length: Maximum allowed length (optional)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, str):
        return False, f"{field_name} must be a string"

    if min_length is not None and len(value) < min_length:
        return False, f"{field_name} must be at least {min_length} characters long"

    if max_length is not None and len(value) > max_length:
        return False, f"{field_name} cannot exceed {max_length} characters"

    return True, None


def validate_numeric_range(value: Any, field_name: str, min_value: float = None, max_value: float = None) -> Tuple[
    bool, Optional[str]]:
    """
    Validate that a numeric value is within the specified range.

    Args:
        value: Numeric value to validate
        field_name: Name of the field (for error message)
        min_value: Minimum allowed value (optional)
        max_value: Maximum allowed value (optional)

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        num_value = float(value)
    except (ValueError, TypeError):
        return False, f"{field_name} must be a number"

    if min_value is not None and num_value < min_value:
        return False, f"{field_name} must be at least {min_value}"

    if max_value is not None and num_value > max_value:
        return False, f"{field_name} cannot exceed {max_value}"

    return True, None


def validate_date_format(date_str: str, format_str: str = "%Y-%m-%d") -> Tuple[bool, Optional[str]]:
    """
    Validate that a string is in the specified date format.

    Args:
        date_str: Date string to validate
        format_str: Expected date format

    Returns:
        Tuple of (is_valid, error_message)
    """
    from datetime import datetime

    if not date_str:
        return False, "Date is required"

    try:
        datetime.strptime(date_str, format_str)
        return True, None
    except ValueError:
        return False, f"Date must be in format {format_str}"


def validate_choices(value: Any, choices: List[Any], field_name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is one of the allowed choices.

    Args:
        value: Value to validate
        choices: List of allowed choices
        field_name: Name of the field (for error message)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if value not in choices:
        choices_str = ", ".join(str(choice) for choice in choices)
        return False, f"{field_name} must be one of: {choices_str}"

    return True, None


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate that a file has an allowed extension.

    Args:
        filename: Name of the file
        allowed_extensions: List of allowed file extensions (without the dot)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "Filename is required"

    # Get file extension (lowercase)
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

    if ext not in allowed_extensions:
        ext_list = ', '.join(allowed_extensions)
        return False, f"File must have one of these extensions: {ext_list}"

    return True, None


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, str]]]:
    """
    Validate data against a JSON schema.

    Args:
        data: Data to validate
        schema: JSON schema definition

    Returns:
        Tuple of (is_valid, error_dict)
    """
    try:
        from jsonschema import validate, ValidationError
        validate(instance=data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, {"error": e.message, "path": list(e.path)}
    except Exception as e:
        return False, {"error": str(e)}